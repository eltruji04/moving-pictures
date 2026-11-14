import random
from datetime import datetime, timedelta

import numpy as np


def get_frames(ra_deg, dec_deg, size_deg):
    # Fake version: ignores its arguments and returns random noise
    n_frames = 8
    side_px = 64
    start_date = datetime(2025, 3, 1)

    rng = np.random.default_rng()
    frames_list = []

    for i in range(n_frames):
        image = rng.normal(size=(side_px, side_px))
        date = start_date + timedelta(days=i * 10)
        wavelength = random.uniform(0.75, 5.0)
        detector = random.randint(1, 6)

        frame = {
            "image": image,
            "date": date,
            "wavelength_um": wavelength,
            "detector": detector,
        }
        frames_list.append(frame)

    return frames_list
