from datetime import datetime
from pathlib import Path

import numpy as np

from core.spherex import _side_in_pixels

# Absolute path built from this file, so it works no matter where the app is launched from
DEMO_DIR = Path(__file__).resolve().parent.parent / "data" / "demo"
DEMO_SIZE_DEG = 0.5  # demo is saved at the largest field; smaller fields are center crops


def demo_name(file_name, track_target):
    """File name (without .npz) of a test object's demo in one view mode."""
    return file_name + ("_follow" if track_target else "_fixed")


def crop_frames(frames, size_deg):
    """Return copies of the frames cut to the central size_deg x size_deg.

    Same pixel scale and same center, so this equals downloading the smaller field.
    """
    if len(frames) == 0:
        return frames
    full_side = frames[0]["image"].shape[0]
    side = min(_side_in_pixels(size_deg), full_side)  # both odd, so the center pixel is kept
    start = (full_side - side) // 2
    return [
        {**frame, "image": frame["image"][start:start + side, start:start + side]}
        for frame in frames
    ]


def save_frames(frames, name):
    if len(frames) == 0:
        return  # np.stack fails on an empty list; nothing to save
    # float32 halves the file size; images are already scaled to 0-1, so no visible loss
    images = np.stack([frame["image"] for frame in frames], axis=0).astype(np.float32)
    dates = [frame["date"].isoformat() for frame in frames]
    wavelengths = [frame["wavelength_um"] for frame in frames]
    detectors = [frame["detector"] for frame in frames]

    DEMO_DIR.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        DEMO_DIR / (name + ".npz"),
        images=images,
        dates=dates,
        wavelengths=wavelengths,
        detectors=detectors,
    )


def load_frames(name):
    path = DEMO_DIR / (name + ".npz")
    if not path.exists():
        return []

    data = np.load(path)
    frames = []
    for k in range(len(data["images"])):
        frames.append({
            "image": data["images"][k],
            "date": datetime.fromisoformat(str(data["dates"][k])),
            "wavelength_um": float(data["wavelengths"][k]),
            "detector": int(data["detectors"][k]),
        })
    return frames
