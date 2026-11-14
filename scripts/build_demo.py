"""Download and save demo frames for the 5 test objects.

Run from the repo root:  python -m scripts.build_demo
Objects already saved in data/demo are skipped, so it can be re-run after IRSA failures.
"""
from core.demo import DEMO_DIR, save_frames
from core.spherex import get_frames
from core.targets import TARGETS

SIZE_DEG = 0.05

for target in TARGETS:
    name = target["file_name"]
    if (DEMO_DIR / (name + ".npz")).exists():
        print(f"{name}: already saved, skipping")
        continue

    print(f"{name}: downloading...", flush=True)
    frames = get_frames(
        target["ra"],
        target["dec"],
        SIZE_DEG,
        pm_ra_mas_yr=target["pm_ra"],
        pm_dec_mas_yr=target["pm_dec"],
    )
    if len(frames) == 0:
        print(f"{name}: NO DATA (or IRSA failed), re-run later")
    else:
        save_frames(frames, name)
        print(f"{name}: {len(frames)} frames saved")
