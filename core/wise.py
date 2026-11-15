"""One older comparison frame from WISE (AllWISE W2, 4.6 µm, 2010) on the same grid as SPHEREx.

WISE has a different resolution and sensitivity, so its brightness is scaled on its own
and can't be compared with SPHEREx; only positions can.
"""
import time

import astropy.units as u
import numpy as np
from astropy.coordinates import SkyCoord
from astropy.io import fits
from astropy.time import Time
from astropy.utils.data import download_file
from astropy.wcs import WCS
from astroquery.ipac.irsa import Irsa
from reproject import reproject_adaptive

from core.spherex import (
    DOWNLOAD_RETRIES,
    FIXED_EPOCH,
    _apply_common_scale,
    _side_in_pixels,
    _target_grid,
)

COLLECTION = "wise_allwise"
BAND = "W2"
WAVELENGTH_UM = 4.6  # W2 nominal wavelength
TELESCOPE = "WISE"
# AllWISE tiles are 1.56° wide, so a large field near a tile edge can be cut off;
# the missing strip shows as black
MIN_COVERAGE = 0.5


def get_wise_frame(ra_deg, dec_deg, size_deg, pm_ra_mas_yr=0.0, pm_dec_mas_yr=0.0, track_target=False):
    """Return one WISE frame dict (same keys as SPHEREx frames plus "telescope"), or None.

    track_target works as in get_frames: False centers on the star's 2026 position
    (so the star appears where it was in 2010), True centers on the star in 2010.
    Raises the last error if the IRSA search fails after all retries.
    """
    target = SkyCoord(
        ra=ra_deg * u.deg,
        dec=dec_deg * u.deg,
        pm_ra_cosdec=pm_ra_mas_yr * u.mas / u.yr,
        pm_dec=pm_dec_mas_yr * u.mas / u.yr,
        obstime=Time("J2000"),
    )
    fixed_center = target.apply_space_motion(new_obstime=FIXED_EPOCH)
    rows = _query_tiles(fixed_center)
    if len(rows) == 0:
        return None

    side_px = _side_in_pixels(size_deg)
    # Near a tile edge the field spans two tiles: build each and combine them (a mosaic)
    tiles = [_build_frame(row, target, fixed_center, size_deg, side_px, track_target) for row in rows]
    tiles = [tile for tile in tiles if tile is not None]
    if not tiles:
        return None

    stack = np.array([np.where(tile["footprint"] > 0, tile["image"], np.nan) for tile in tiles])
    covered = np.any(np.isfinite(stack), axis=0)
    if covered.mean() < MIN_COVERAGE:
        return None

    frame = tiles[0]
    frame["image"] = np.nanmean(np.where(covered, stack, 0.0), axis=0)
    frame["image"][~covered] = np.nan
    del frame["footprint"]
    _apply_common_scale([frame])  # its own brightness scale
    return frame


def _query_tiles(center):
    for attempt in range(DOWNLOAD_RETRIES):
        try:
            results = Irsa.query_sia(pos=(center, 1 * u.arcsec), collection=COLLECTION)
            break
        except Exception:
            if attempt < DOWNLOAD_RETRIES - 1:
                time.sleep(3)
            else:
                raise
    keep = (results["energy_bandpassname"] == BAND) & (results["dataproduct_subtype"] == "science")
    results = results[keep]
    if len(results) > 1 and "s_ra" in results.colnames:
        tile_centers = SkyCoord(ra=results["s_ra"], dec=results["s_dec"], unit="deg")
        results = results[np.argsort(center.separation(tile_centers).deg)]
    return results


def _build_frame(row, target, fixed_center, size_deg, side_px, track_target):
    # The AllWISE image is a stack of exposures from t_min to t_max; use the middle
    obs_time = Time((float(row["t_min"]) + float(row["t_max"])) / 2, format="mjd")
    star = target.apply_space_motion(new_obstime=obs_time)
    center = star if track_target else fixed_center

    url = f"{row['access_url']}?center={center.ra.deg},{center.dec.deg}&size={size_deg * 1.5}"
    path = None
    for attempt in range(DOWNLOAD_RETRIES):
        try:
            path = download_file(url, cache=True)
            break
        except Exception:
            time.sleep(2 * (attempt + 1))
    if path is None:
        return None

    with fits.open(path) as hdul:
        data = hdul[0].data.astype(float)
        source_wcs = WCS(hdul[0].header)
        # WISE pixels (1.375") are much smaller than SPHEREx's (6.15"): adaptive resampling
        # averages them instead of picking single noisy pixels
        image, footprint = reproject_adaptive(
            (data, source_wcs), _target_grid(center, side_px), shape_out=(side_px, side_px)
        )

    return {
        "image": image,
        "date": obs_time.to_datetime(),
        "wavelength_um": WAVELENGTH_UM,
        "detector": 0,
        "telescope": TELESCOPE,
        "footprint": footprint,
    }
