from datetime import datetime
from pathlib import Path

import numpy as np

# Absolute path built from this file, so it works no matter where the app is launched from
DEMO_DIR = Path(__file__).resolve().parent.parent / "data" / "demo"


def save_frames(frames, name):
    if len(frames) == 0:
        return  # np.stack fails on an empty list; nothing to save
    images = np.stack([frame["image"] for frame in frames], axis=0)
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
