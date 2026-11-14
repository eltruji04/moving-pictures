"""Exploration script: download one SPHEREx cutout of Barnard's Star and inspect its FITS header.

Run from the repo root:  python scripts/explore_fits.py
Not part of the app; only for understanding the data.
"""
import astropy.units as u
from astropy.coordinates import SkyCoord
from astropy.io import fits
from astropy.utils.data import download_file
from astroquery.ipac.irsa import Irsa

# Barnard's Star, approximate J2000 coordinates (verify in SIMBAD)
RA_DEG = 269.452
DEC_DEG = 4.693
CUTOUT_SIZE_DEG = 0.05
COLLECTION = "spherex_dr1"

KEYWORDS_OF_INTEREST = ("DATE", "MJD", "TIME", "WAVE", "LAMB", "DET", "BAND", "EXP")

coord = SkyCoord(RA_DEG, DEC_DEG, unit="deg")
results = Irsa.query_sia(pos=(coord, 1 * u.arcsec), collection=COLLECTION)
print(f"{len(results)} images found in {COLLECTION}")

results.sort("t_min")
first = results[0]
print("t_min (MJD):", first["t_min"], "| em_min/em_max (m):", first["em_min"], first["em_max"])

cutout_url = f"{first['access_url']}?center={RA_DEG},{DEC_DEG}&size={CUTOUT_SIZE_DEG}"
print("Cutout URL:", cutout_url)

local_path = download_file(cutout_url, cache=True)

with fits.open(local_path) as hdul:
    print("\n=== HDUs in the file ===")
    hdul.info()

    for index, hdu in enumerate(hdul):
        print(f"\n=== HDU {index} ({hdu.name}): keywords of interest ===")
        for key, value in hdu.header.items():
            if any(word in key for word in KEYWORDS_OF_INTEREST):
                print(f"  {key:10} = {value!r:30}  / {hdu.header.comments[key]}")

    # Save every header to a text file to read calmly
    with open("scripts/header_dump.txt", "w") as out:
        for index, hdu in enumerate(hdul):
            out.write(f"===== HDU {index} ({hdu.name}) =====\n")
            out.write(hdu.header.tostring(sep="\n"))
            out.write("\n\n")
    print("\nFull headers saved to scripts/header_dump.txt")
