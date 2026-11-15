"""Parse RA/Dec typed by the user, in decimal degrees or sexagesimal."""
import astropy.units as u
from astropy.coordinates import SkyCoord


def parse_coords(text):
    """Return (ra_deg, dec_deg), or None if the text can't be read.

    Accepts "269.452 4.693", "269.452, 4.693", "17:57:48.5 +04:41:36",
    "17h57m48.5s +04d41m36s" and "17 57 48.5 +04 41 36".
    """
    text = text.replace(",", " ").strip()

    # The unit must be chosen here: astropy reads "17:57:48.5" as degrees without
    # complaining if told so, giving a wrong RA (17.96 instead of 269.45)
    is_sexagesimal = ":" in text or "h" in text.lower() or len(text.split()) > 2
    unit = (u.hourangle, u.deg) if is_sexagesimal else (u.deg, u.deg)

    try:
        coord = SkyCoord(text, unit=unit)
    except Exception:
        return None
    return coord.ra.deg, coord.dec.deg
