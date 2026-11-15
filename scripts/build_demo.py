"""Download and save demo frames for the 5 test objects, in both view modes.

Run from the repo root:  python -m scripts.build_demo
Files already saved in data/demo are skipped, so it can be re-run after IRSA failures.
"""
from core.demo import DEMO_DIR, DEMO_SIZE_DEG, demo_name, save_frames, wise_name
from core.spherex import get_frames
from core.targets import TARGETS
from core.wise import get_wise_frame

for target in TARGETS:
    for track_target in (False, True):
        name = demo_name(target["file_name"], track_target)
        if (DEMO_DIR / (name + ".npz")).exists():
            print(f"{name}: already saved, skipping")
            continue

        print(f"{name}: downloading...", flush=True)
        try:
            frames = get_frames(
                target["ra"],
                target["dec"],
                DEMO_SIZE_DEG,
                pm_ra_mas_yr=target["pm_ra"],
                pm_dec_mas_yr=target["pm_dec"],
                track_target=track_target,
            )
        except Exception as error:
            print(f"{name}: IRSA failed ({error}), re-run later")
            continue
        if len(frames) == 0:
            print(f"{name}: NO DATA")
        else:
            save_frames(frames, name)
            print(f"{name}: {len(frames)} frames saved")

# One WISE (2010) comparison frame per object and view mode
for target in TARGETS:
    for track_target in (False, True):
        name = wise_name(target["file_name"], track_target)
        if (DEMO_DIR / (name + ".npz")).exists():
            print(f"{name}: already saved, skipping")
            continue
        print(f"{name}: downloading...", flush=True)
        try:
            frame = get_wise_frame(
                target["ra"], target["dec"], DEMO_SIZE_DEG,
                pm_ra_mas_yr=target["pm_ra"], pm_dec_mas_yr=target["pm_dec"],
                track_target=track_target,
            )
        except Exception as error:
            print(f"{name}: IRSA failed ({error}), re-run later")
            continue
        if frame is None:
            print(f"{name}: NO WISE DATA")
        else:
            save_frames([frame], name)
            print(f"{name}: saved")
