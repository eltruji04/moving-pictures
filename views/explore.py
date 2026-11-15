import streamlit as st
import numpy as np
from core.spherex import get_frames
from core.targets import TARGETS, proper_motion_for
from core.demo import crop_frames, demo_name, load_frames
from core.animate import average_by_visit, make_blink_gif, make_difference_image
from core.coords import parse_coords


DISPLAY_WIDTH_PX = 600  # images are zoomed by a whole number to about this width (sharp, no blur)
FIELD_SIZES = {"Close (0.1°)": 0.1, "Medium (0.2°)": 0.2, "Far (0.5°)": 0.5}

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
field = st.radio("Field of view", list(FIELD_SIZES), horizontal=True,
                 help="Close shows the motion best; Far shows more background stars.")
size_deg = FIELD_SIZES[field]
FIXED_SKY = "Fixed sky: watch the star move"
FOLLOW_STAR = "Follow the star: the background moves"
mode = st.radio("View", [FIXED_SKY, FOLLOW_STAR], horizontal=True)
st.caption("Demo objects update at once; for a live search, search again after changing the view.")


st.subheader("Try a test object (saved demo data)")
columns = st.columns(5)
for column, target in zip(columns, TARGETS):
    with column:
        if st.button(target["label"]):
            st.session_state["demo_target"] = target
            st.session_state["source"] = "demo"


if st.button("Search SPHEREx live (~1 min)", disabled=coords is None):
    bar = st.progress(0, text="Searching SPHEREx...")

    def update_bar(done, total):
        bar.progress(done / total, text=f"Downloaded {done} of {total} cutouts")

    try:
        with st.spinner("Downloading SPHEREx images..."):
            pm_ra, pm_dec = proper_motion_for(ra, dec)  # 0, 0 unless it's a test object
            frames = get_frames(
                ra, dec, size_deg, pm_ra, pm_dec,
                on_progress=update_bar,
                track_target=(mode == FOLLOW_STAR),
            )
    except Exception as error:
        bar.empty()
        st.session_state.pop("frames", None)  # don't keep showing an old result
        st.error(
            "IRSA (the SPHEREx archive) is not responding right now. "
            "Try again in a minute, or use the demo objects above."
        )
        st.caption(f"Details: {type(error).__name__}: {error}")
    else:
        bar.empty()
        st.session_state["frames"] = frames
        st.session_state["live_size_deg"] = size_deg
        st.session_state["source"] = "live"


frames = None
if st.session_state.get("source") == "demo":
    # Demo is saved at 0.5° in both views, so the view and field options apply at once
    target = st.session_state["demo_target"]
    saved = load_frames(demo_name(target["file_name"], mode == FOLLOW_STAR))
    frames = crop_frames(saved, size_deg)
    st.info(f"DEMO MODE: saved SPHEREx data for {target['label']}.")
elif st.session_state.get("source") == "live" and "frames" in st.session_state:
    frames = st.session_state["frames"]
    if size_deg <= st.session_state["live_size_deg"]:
        frames = crop_frames(frames, size_deg)
    else:
        st.caption("Search again to download this larger field.")

if frames is not None:
    if len(frames) == 0:
        st.warning("No SPHEREx data found for this position")
    else:
        zoom = max(1, DISPLAY_WIDTH_PX // frames[0]["image"].shape[0])
        gif = make_blink_gif(frames, zoom=zoom)
        st.image(gif)
        i = st.slider("Frame", 0, len(frames) - 1, 0)
        frame = frames[i]

        image = np.flipud(frame["image"])  # row 0 is drawn at the top; flip so north is up
        image = np.repeat(np.repeat(image, zoom, axis=0), zoom, axis=1)
        st.image(image, clamp=True)
        st.caption(
            f"{frame['date']:%Y-%m-%d %H:%M} UTC · "
            f"λ = {frame['wavelength_um']:.2f} µm · detector {frame['detector']}"
        )

        st.subheader("Difference: what changed between two dates")
        compare = st.radio(
            "Compare", ["Visits (averaged, less noise)", "Two single frames"], horizontal=True,
            help="Averaging all frames of a visit removes most noise, cosmic rays and satellite "
                 "trails, but mixes slightly different wavelengths.",
        )
        options = average_by_visit(frames) if compare.startswith("Visits") else frames
        labels = [
            f"{f['date']:%Y-%m-%d} · {f['wavelength_um']:.2f} µm"
            + (f" · {f['n_frames']} frames" if "n_frames" in f else "")
            for f in options
        ]
        later_default = len(options) - 1
        if compare.startswith("Visits") and len(options) > 1:
            # The later visit with the most frames has the least noise
            later_default = 1 + int(np.argmax([f["n_frames"] for f in options[1:]]))
        col_a, col_b = st.columns(2)
        with col_a:
            a = st.selectbox("Earlier", range(len(options)), index=0, format_func=lambda k: labels[k])
        with col_b:
            b = st.selectbox("Later", range(len(options)), index=later_default,
                             format_func=lambda k: labels[k])
        st.image(make_difference_image(options[a], options[b], zoom=zoom))
        st.caption(
            "Later minus earlier. What stayed the same turns black. A star that moved leaves "
            "blue where it was and orange where it went. Brightness changes can also come from "
            "the different wavelength of each frame, and single dots are usually cosmic rays."
        )
        if mode == FOLLOW_STAR:
            st.warning("In 'Follow the star' the star is kept centered, so here the background "
                       "stars are what moves. Switch to 'Fixed sky' to see the star's own motion.")
