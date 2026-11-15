import streamlit as st
import numpy as np
from core.spherex import get_frames
from core.targets import TARGETS
from core.demo import load_frames
from core.animate import make_blink_gif
from core.coords import parse_coords


DISPLAY_ZOOM = 12  # each SPHEREx pixel is shown as a 12x12 block (sharp, no blur)

st.set_page_config(
    page_title="Moving pictures",
    page_icon="🔭",
    layout="wide",
)

st.title("Explorador estelar")

coords_text = st.text_input(
    "Coordinates (RA Dec)",
    value="269.452 4.693",
    help="Decimal degrees (269.452 4.693) or sexagesimal (17:57:48.5 +04:41:36)",
)
coords = parse_coords(coords_text)
if coords is None:
    st.error("Can't read those coordinates. Try 269.452 4.693 or 17:57:48.5 +04:41:36")
else:
    ra, dec = coords
    st.caption(f"Read as RA = {ra:.4f}°, Dec = {dec:.4f}°")
size_deg = st.number_input("Field size (deg)", value=0.05, format="%.3f")


st.subheader("Try a test object (saved demo data)")
columns = st.columns(5)
for column, target in zip(columns, TARGETS):
    with column:
        if st.button(target["label"]):
            st.session_state["frames"] = load_frames(target["file_name"]) 
            st.session_state["source"] = "demo: " + target["label"]


if st.button("Search SPHEREx live (~3 min)", disabled=coords is None):
    with st.spinner("Downloading SPHEREx images..."):
        frames = get_frames(ra, dec, size_deg)
    st.session_state["frames"] = frames
    st.session_state["source"] = "live"


if "frames" in st.session_state:
    frames = st.session_state["frames"]

    if len(frames) == 0:
        st.warning("No SPHEREx data found for this position")
    else:
        if st.session_state["source"].startswith("demo"):
            st.info("DEMO MODE: saved data, field size fixed at 0.05°.")
        gif = make_blink_gif(frames)
        st.image(gif)
        i = st.slider("Frame", 0, len(frames) - 1, 0)
        frame = frames[i]

        image = np.flipud(frame["image"])  # row 0 is drawn at the top; flip so north is up
        image = np.repeat(np.repeat(image, DISPLAY_ZOOM, axis=0), DISPLAY_ZOOM, axis=1)
        st.image(image, clamp=True)
        st.caption(
            f"{frame['date']:%Y-%m-%d %H:%M} UTC · "
            f"λ = {frame['wavelength_um']:.2f} µm · detector {frame['detector']}"
        )
