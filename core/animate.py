from PIL import Image, ImageDraw, ImageFont
import numpy as np
import io

CROSS_GAP_PX = 30  # empty space around the center, so the cross doesn't cover the target
CROSS_ARM_PX = 55  # each arm goes from CROSS_GAP_PX to CROSS_ARM_PX away from the center
LABEL_FONT_SIZE = 16


def make_blink_gif(frames, zoom=12, ms_per_frame=500):
    """Return a GIF of the frames, with each SPHEREx pixel shown as a zoom x zoom block.

    frames: list of dicts, each with keys "image", "date", "wavelength_um", "detector"
    zoom: how many pixels to show per SPHEREx pixel
    ms_per_frame: how long to show each frame in milliseconds
    Returns the GIF as bytes, or None if there are no frames.
    """
    if len(frames) == 0:
        return None

    font = ImageFont.load_default(size=LABEL_FONT_SIZE)
    images = []
    for frame in frames:
        image = np.flipud(frame["image"])
        image = np.repeat(np.repeat(image, zoom, axis=0), zoom, axis=1)
        image = np.clip(image, 0, 1) * 255
        image = Image.fromarray(image.astype(np.uint8)).convert("RGB")

        draw = ImageDraw.Draw(image)
        _draw_cross(draw, image.width // 2, image.height // 2)
        # ASCII only: the bundled font may not have λ or µ
        label = f"{frame['date']:%Y-%m-%d}   {frame['wavelength_um']:.2f} um"
        draw.text((8, 6), label, fill="yellow", font=font)

        images.append(image)

    gif_bytes = io.BytesIO()
    images[0].save(
        gif_bytes,
        format="GIF",
        save_all=True,
        append_images=images[1:],
        duration=ms_per_frame,
        loop=0,
    )
    return gif_bytes.getvalue()


POSITIVE_COLOR = np.array([1.0, 0.6, 0.1])  # brighter in the later frame: orange
NEGATIVE_COLOR = np.array([0.2, 0.6, 1.0])  # brighter in the earlier frame: blue
DIFF_SCALE_PERCENTILE = 99.9  # this |difference| maps to full color


VISIT_GAP_DAYS = 30  # frames closer than this in time belong to the same visit


def average_by_visit(frames):
    """Group frames (sorted by date) into visits and return one averaged frame per visit.

    Averaging lowers the noise and washes out cosmic rays and satellite trails,
    but mixes the wavelengths of the frames in each visit.
    """
    visits = []
    for frame in frames:
        if visits and (frame["date"] - visits[-1][-1]["date"]).days < VISIT_GAP_DAYS:
            visits[-1].append(frame)
        else:
            visits.append([frame])
    return [
        {
            "image": np.mean([f["image"] for f in visit], axis=0),
            "date": visit[0]["date"],
            "wavelength_um": float(np.mean([f["wavelength_um"] for f in visit])),
            "detector": visit[0]["detector"],
            "n_frames": len(visit),
        }
        for visit in visits
    ]


def make_difference_image(frame_a, frame_b, zoom=12):
    """Return a PIL image of frame_b minus frame_a, with a cross at the center.

    Anything that stayed the same cancels out (black). Where a star moved, the
    old position shows in blue and the new one in orange.
    """
    difference = np.flipud(frame_b["image"] - frame_a["image"])  # flip so north is up
    scale = np.nanpercentile(np.abs(difference), DIFF_SCALE_PERCENTILE)
    if not scale > 0:
        scale = 1.0  # identical frames: avoid dividing by zero
    amount = np.clip(difference / scale, -1, 1)

    rgb = (
        np.clip(amount, 0, 1)[..., None] * POSITIVE_COLOR
        + np.clip(-amount, 0, 1)[..., None] * NEGATIVE_COLOR
    )
    rgb = np.nan_to_num(rgb)
    rgb = np.repeat(np.repeat(rgb, zoom, axis=0), zoom, axis=1)
    image = Image.fromarray((rgb * 255).astype(np.uint8))

    _draw_cross(ImageDraw.Draw(image), image.width // 2, image.height // 2)
    return image


def _draw_cross(draw, cx, cy):
    """Four short red arms around (cx, cy), leaving the center empty."""
    for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
        start = (cx + dx * CROSS_GAP_PX, cy + dy * CROSS_GAP_PX)
        end = (cx + dx * CROSS_ARM_PX, cy + dy * CROSS_ARM_PX)
        draw.line([start, end], fill="red", width=2)
