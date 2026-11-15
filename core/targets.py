"""The 5 required test objects. Positions (J2000) and proper motions (mas/yr) from SIMBAD,
queried 2026-11-14 via the Harvard mirror."""
import astropy.units as u
from astropy.coordinates import SkyCoord

TARGETS = [
    {
        "file_name": "barnard",
        "label": "Barnard's Star",
        "ra": 269.4520769586187,
        "dec": 4.693364966576667,
        "pm_ra": -801.551,
        "pm_dec": 10362.394,
    },
    {
        "file_name": "eps_ind_b",
        "label": "Epsilon Indi B",
        "ra": 331.04414658852124,
        "dec": -56.782844195116105,
        "pm_ra": 3981.977,
        "pm_dec": -2466.832,
    },
    {
        "file_name": "wise_0855",
        "label": "WISE 0855−0714",
        "ra": 133.81890825,
        "dec": -7.247048,  # SIMBAD position from a WISE catalog: epoch may not be J2000 (unverified)
        "pm_ra": -8123.7,
        "pm_dec": 673.2,
    },
    {
        "file_name": "rw_aur",
        "label": "RW Aurigae",
        "ra": 76.95652603458333,
        "dec": 30.401438173888888,
        "pm_ra": 7.23,
        "pm_dec": -20.33,
    },
    {
        "file_name": "r_dra",
        "label": "R Draconis",
        "ra": 248.16761083295,
        "dec": 66.75497941722,
        "pm_ra": -20.643,
        "pm_dec": 6.149,
    },
]


MATCH_RADIUS_ARCMIN = 1.0  # typed coordinates this close to a test object use its proper motion


def proper_motion_for(ra_deg, dec_deg):
    """Return (pm_ra, pm_dec) in mas/yr of the test object at these J2000 coordinates, or (0, 0)."""
    typed = SkyCoord(ra=ra_deg * u.deg, dec=dec_deg * u.deg)
    for target in TARGETS:
        known = SkyCoord(ra=target["ra"] * u.deg, dec=target["dec"] * u.deg)
        if typed.separation(known) < MATCH_RADIUS_ARCMIN * u.arcmin:
            return target["pm_ra"], target["pm_dec"]
    return 0.0, 0.0
