"""Real get_frames: SPHEREx cutouts from IRSA, aligned on a common north-up grid."""
import time
import warnings

import astropy.units as u
import numpy as np
from astropy import log
from astropy.coordinates import SkyCoord
from astropy.io import fits
from astropy.time import Time
from astropy.utils.data import download_file
from astropy.visualization import AsinhStretch
from astropy.wcs import WCS
from astroquery.ipac.irsa import Irsa
from reproject import reproject_interp
from scipy.ndimage import maximum_filter

COLLECTION = "spherex_dr1"
PIXEL_SCALE_ARCSEC = 6.15
MWIR_MIN_WAVELENGTH_M = 3e-6  # em_min above this = MWIR detectors (4-6)
DOWNLOAD_RETRIES = 3
MIN_COVERAGE = 0.9  # drop frames whose cutout covers less than 90% of the grid
ASINH_SOFTENING = 0.002  # smaller = more boost for faint pixels (0.002 chosen visually on Barnard)

warnings.simplefilter("ignore")  # SPHEREx headers trigger harmless SIP/WCS warnings
log.setLevel("ERROR")


def get_frames(ra_deg, dec_deg, size_deg, pm_ra_mas_yr=0.0, pm_dec_mas_yr=0.0, n_frames=12):
    """Return aligned SPHEREx frames around a position.

    ra_deg, dec_deg: J2000 coordinates. pm_*: proper motion in mas/yr (0 for fixed targets).
    Returns [] if nothing is found.
    """
    target = SkyCoord(
        ra=ra_deg * u.deg,
        dec=dec_deg * u.deg,
        pm_ra_cosdec=pm_ra_mas_yr * u.mas / u.yr,
        pm_dec=pm_dec_mas_yr * u.mas / u.yr,
        obstime=Time("J2000"),
    )

    rows = _query_images(target)
    if len(rows) == 0:
        return []

    side_px = _side_in_pixels(size_deg)
    frames = []
    for row in _spread_in_time(rows, n_frames):
        frame = _build_frame(row, target, size_deg, side_px)
        if frame is not None:
            frames.append(frame)

    _fill_holes(frames)  # must run before scaling, which turns any remaining NaN into 0
    _apply_common_scale(frames)
    return frames


def _fill_holes(frames):
    """Fill empty (NaN) pixels with the brightest neighbor in a 5x5 window.

    Saturated star cores become bright; isolated bad pixels blend into the background.
    """
    for frame in frames:
        image = frame["image"]
        holes = np.isnan(image)  # True where the pixel is empty
        if not holes.any():
            continue

        filled = np.copy(image)
        filled[holes] = -np.inf  # so an empty pixel never wins the maximum
        neighbor_max = maximum_filter(filled, size=5)
        image[holes] = neighbor_max[holes]
        frame["image"] = image


def _query_images(target):
    # Search near the target's position around the middle of the mission
    position_now = target.apply_space_motion(new_obstime=Time("2026-01-01"))


    for attempt in range(DOWNLOAD_RETRIES):
        try:
            results = Irsa.query_sia(pos=(position_now, 1 * u.arcsec), collection=COLLECTION)
            results = results[results["em_min"] > MWIR_MIN_WAVELENGTH_M]
            results.sort("t_min")
            return results
        
        except Exception:
            if attempt < DOWNLOAD_RETRIES - 1:
                time.sleep(3)
            else:
                return []


def _spread_in_time(rows, n_frames):
    if len(rows) <= n_frames:
        return list(rows)
    indices = np.unique(np.linspace(0, len(rows) - 1, n_frames).astype(int))
    return [rows[i] for i in indices]


def _side_in_pixels(size_deg):
    side = int(round(size_deg * 3600 / PIXEL_SCALE_ARCSEC))
    return side if side % 2 == 1 else side + 1  # odd, so the target sits on the central pixel


def _target_grid(position, side_px):
    grid = WCS(naxis=2)
    grid.wcs.ctype = ["RA---TAN", "DEC--TAN"]
    grid.wcs.crval = [position.ra.deg, position.dec.deg]
    grid.wcs.crpix = [(side_px + 1) / 2, (side_px + 1) / 2]
    grid.wcs.cdelt = [-PIXEL_SCALE_ARCSEC / 3600, PIXEL_SCALE_ARCSEC / 3600]  # north up, east left
    return grid


def _download(url):
    for attempt in range(DOWNLOAD_RETRIES):
        try:
            return download_file(url, cache=True)
        except Exception:
            time.sleep(2 * (attempt + 1))
    return None


def _build_frame(row, target, size_deg, side_px):
    obs_time = Time(row["t_min"], format="mjd")
    position = target.apply_space_motion(new_obstime=obs_time)

    # Download a bit more than needed so rotated cutouts still cover the grid corners
    cutout_size = size_deg * 1.5
    url = f"{row['access_url']}?center={position.ra.deg},{position.dec.deg}&size={cutout_size}"
    path = _download(url)
    if path is None:
        return None

    with fits.open(path) as hdul:
        header = hdul["IMAGE"].header
        source_wcs = WCS(header)
        image, footprint = reproject_interp(
            (hdul["IMAGE"].data, source_wcs), _target_grid(position, side_px), shape_out=(side_px, side_px)
        )
        x, y = source_wcs.world_to_pixel(position)
        wavelength_wcs = WCS(header, fobj=hdul, key="W")
        wavelength_um, _bandwidth = wavelength_wcs.pixel_to_world_values(x, y)
        date = Time(header["DATE-OBS"], scale="utc").to_datetime()
        detector = int(header["DETECTOR"])

    if footprint.mean() < MIN_COVERAGE:
        return None

    return {
        "image": image,
        "date": date,
        "wavelength_um": float(wavelength_um),
        "detector": detector,
    }


def _apply_common_scale(frames):
    """Normalize all images to 0-1 with the same limits and an asinh stretch.

    asinh is linear for faint pixels and logarithmic for bright ones, so faint
    background stars stay visible next to a very bright target.
    """
    if not frames:
        return
    # Each frame has its own sky level (different wavelength, zodiacal light), so subtract
    # each frame's median first; then the background sits at 0 in every frame
    for frame in frames:
        frame["image"] = frame["image"] - np.nanmedian(frame["image"])
    all_pixels = np.concatenate([f["image"].ravel() for f in frames])
    low = 0.0
    high = np.nanpercentile(all_pixels, 99.5)
    stretch = AsinhStretch(a=ASINH_SOFTENING)
    for frame in frames:
        scaled = np.clip((frame["image"] - low) / (high - low), 0, 1)
        frame["image"] = np.nan_to_num(stretch(scaled), nan=0.0)
