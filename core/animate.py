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


def _draw_cross(draw, cx, cy):
    """Four short red arms around (cx, cy), leaving the center empty."""
    for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
        start = (cx + dx * CROSS_GAP_PX, cy + dy * CROSS_GAP_PX)
        end = (cx + dx * CROSS_ARM_PX, cy + dy * CROSS_ARM_PX)
        draw.line([start, end], fill="red", width=2)
