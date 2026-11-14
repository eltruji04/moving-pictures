import streamlit as st
import numpy as np
from core.frames import get_frames

DISPLAY_ZOOM = 12  # each SPHEREx pixel is shown as a 12x12 block (sharp, no blur)

st.set_page_config(
    page_title="Moving pictures",
    page_icon="🔭",
    layout="wide",
)

st.title("Explorador estelar")

ra = st.number_input("RA (deg)", value=269.452, format="%.4f")
dec = st.number_input("Dec (deg)", value=4.693, format="%.4f")
size_deg = st.number_input("Field size (deg)", value=0.05, format="%.3f")

if st.button("Barnard's Star"):
    with st.spinner("Downloading SPHEREx images..."):
        frames = get_frames(ra, dec, size_deg)
        # With the real backend (core.spherex), also pass:
        # pm_ra_mas_yr=-801.551, pm_dec_mas_yr=10362.394
    st.session_state["frames"] = frames

if "frames" in st.session_state:
    frames = st.session_state["frames"]

    if len(frames) == 0:
        st.warning("No SPHEREx data found for this position")
    else:
        i = st.slider("Frame", 0, len(frames) - 1, 0)
        frame = frames[i]

        image = np.flipud(frame["image"])  # row 0 is drawn at the top; flip so north is up
        image = np.repeat(np.repeat(image, DISPLAY_ZOOM, axis=0), DISPLAY_ZOOM, axis=1)
        st.image(image, clamp=True)
        st.caption(
            f"{frame['date']:%Y-%m-%d %H:%M} UTC · "
            f"λ = {frame['wavelength_um']:.2f} µm · detector {frame['detector']}"
        )
