import streamlit as st
import numpy as np
from core.spherex import get_frames
from core.targets import TARGETS, proper_motion_for
from core.demo import crop_frames, demo_name, load_frames, wise_name
from core.wise import get_wise_frame
from core.animate import average_by_visit, make_blink_gif, make_difference_image
from core.coords import parse_coords


DISPLAY_WIDTH_PX = 600  # images are zoomed by a whole number to about this width (sharp, no blur)
FIELD_SIZES = {"Close (0.1°)": 0.1, "Medium (0.2°)": 0.2, "Far (0.5°)": 0.5}

st.title("Explore the sky")
st.caption("Pick an object (or any position), choose how to look at it, and watch the blink.")

def select_demo(target):
    # Runs before the page reruns, so the clicked button is already highlighted
    st.session_state["demo_target"] = target
    st.session_state["source"] = "demo"


with st.container(border=True):
    st.markdown("#### 1 · Choose a target")
    st.caption("Demo objects: saved data, instant.")
    for column, target in zip(st.columns(len(TARGETS)), TARGETS):
        is_selected = (st.session_state.get("source") == "demo"
                       and st.session_state["demo_target"]["file_name"] == target["file_name"])
        with column:
            st.button(target["label"], width="stretch", on_click=select_demo, args=(target,),
                      type="primary" if is_selected else "secondary")

    with st.expander("**…or type any sky position** (live search, ~1 min)", expanded=True):
        input_col, _ = st.columns([3, 2])
        with input_col:
            coords_text = st.text_input("Coordinates (RA Dec)", value="269.452 4.693")
        st.caption("Decimal degrees (269.452 4.693) or sexagesimal (17:57:48.5 +04:41:36)")
        coords = parse_coords(coords_text)
        if coords is None:
            st.error("Can't read those coordinates. Try 269.452 4.693 or 17:57:48.5 +04:41:36")
        else:
            ra, dec = coords
            st.caption(f"Read as RA = {ra:.4f}°, Dec = {dec:.4f}°")
        search_clicked = st.button("Search SPHEREx live (~1 min)", icon="🛰️", type="primary",
                                   disabled=coords is None)
        st.caption("After changing the view or field, search again to update a live result.")

with st.container(border=True):
    st.markdown("#### 2 · How to look at it")
    field_col, view_col, wise_col = st.columns([3, 3, 4], gap="large")
    with field_col:
        field = st.radio("Field of view", list(FIELD_SIZES), horizontal=True,
                         help="Close shows the motion best; Far shows more background stars.")
        size_deg = FIELD_SIZES[field]
    with view_col:
        FIXED_SKY = "Fixed sky: watch the star move"
        FOLLOW_STAR = "Follow the star: the background moves"
        mode = st.radio("View", [FIXED_SKY, FOLLOW_STAR])
    with wise_col:
        include_wise = st.checkbox(
            "Add an older image from WISE (2010)",
            help="WISE is another infrared telescope. Its brightness is scaled on its own "
                 "and can't be compared with SPHEREx.",
        )
        st.caption("15 years earlier: makes slow motion easier to see.")


if search_clicked:
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
            wise_frame = None
            if include_wise:
                bar.progress(1.0, text="Searching WISE...")
                wise_frame = get_wise_frame(
                    ra, dec, size_deg, pm_ra, pm_dec, track_target=(mode == FOLLOW_STAR)
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
        st.session_state["live_wise"] = [wise_frame] if wise_frame is not None else []
        st.session_state["live_has_wise"] = include_wise
        st.session_state["live_size_deg"] = size_deg
        st.session_state["source"] = "live"


frames = None
if st.session_state.get("source") == "demo":
    # Demo is saved at 0.5° in both views, so the view and field options apply at once
    target = st.session_state["demo_target"]
    saved = load_frames(demo_name(target["file_name"], mode == FOLLOW_STAR))
    frames = crop_frames(saved, size_deg)
    if include_wise and frames:
        wise = load_frames(wise_name(target["file_name"], mode == FOLLOW_STAR), telescope="WISE")
        frames = crop_frames(wise, size_deg) + frames
    span = ""
    if frames:
        first = min(f["date"] for f in frames)
        last = max(f["date"] for f in frames)
        span = f" ({len(frames)} frames, {first:%b %Y} – {last:%b %Y})"
    st.info(f"**DEMO MODE** · Showing saved data for **{target['label']}**{span}. "
            "Nothing is downloaded.", icon="💾")
elif st.session_state.get("source") == "live" and "frames" in st.session_state:
    frames = st.session_state["frames"]
    if include_wise and frames:
        if not st.session_state.get("live_has_wise"):
            st.caption("Search again to add the WISE image.")
        elif not st.session_state["live_wise"]:
            st.caption("No WISE image covers this field.")
        frames = st.session_state["live_wise"] + frames
    if size_deg <= st.session_state["live_size_deg"]:
        frames = crop_frames(frames, size_deg)
    else:
        st.caption("Search again to download this larger field.")

if frames is not None:
    if len(frames) == 0:
        st.warning("No SPHEREx data found for this position")
    else:
        zoom = max(1, DISPLAY_WIDTH_PX // frames[0]["image"].shape[0])
        st.subheader("3 · Watch the blink")
        blink_col, frame_col = st.columns(2, gap="large")
        with blink_col:
            gif_slot = st.empty()  # the GIF goes above the speed control, but needs its value
            speed = st.segmented_control(
                "Blink speed", ["Slow", "Medium", "Fast"], default="Medium", required=True,
                help="Use the Frame slider on the right to pause on a single frame.",
            )
            ms_per_frame = {"Slow": 1000, "Medium": 500, "Fast": 200}[speed or "Medium"]
            gif_slot.image(make_blink_gif(frames, zoom=zoom, ms_per_frame=ms_per_frame))
            st.caption("The cross marks the target. Every frame shows its date and wavelength.")
        with frame_col:
            i = st.slider("Frame", 0, len(frames) - 1, 0)
            frame = frames[i]

            image = np.flipud(frame["image"])  # row 0 is drawn at the top; flip so north is up
            image = np.repeat(np.repeat(image, zoom, axis=0), zoom, axis=1)
            st.image(image, clamp=True)
            st.caption(
                f"{frame['date']:%Y-%m-%d %H:%M} UTC · "
                f"{frame.get('telescope', 'SPHEREx')} · λ = {frame['wavelength_um']:.2f} µm"
                + (f" · detector {frame['detector']}" if frame.get("telescope", "SPHEREx") == "SPHEREx" else "")
            )

        with st.expander(f"All {len(frames)} frames: date and wavelength"):
            st.dataframe(
                [
                    {
                        "Frame": k,
                        "Date (UTC)": f"{f['date']:%Y-%m-%d %H:%M}",
                        "Telescope": f.get("telescope", "SPHEREx"),
                        "Wavelength (µm)": round(f["wavelength_um"], 2),
                        "Detector": f["detector"] if f.get("telescope", "SPHEREx") == "SPHEREx" else None,
                    }
                    for k, f in enumerate(frames)
                ],
                hide_index=True,
            )
            st.caption("Each SPHEREx frame sees a slightly different wavelength (color of infrared), "
                       "so some brightness changes between frames are color, not real variation.")

        st.divider()
        st.subheader("4 · Difference: what changed between two dates")
        compare = st.radio(
            "Compare", ["Visits (averaged, less noise)", "Two single frames"], horizontal=True,
            help="Averaging all frames of a visit removes most noise, cosmic rays and satellite "
                 "trails, but mixes slightly different wavelengths.",
        )
        options = average_by_visit(frames) if compare.startswith("Visits") else frames
        labels = [
            f"{f.get('telescope', 'SPHEREx')} {f['date']:%Y-%m-%d} · {f['wavelength_um']:.2f} µm"
            + (f" · {f['n_frames']} frames" if "n_frames" in f else "")
            for f in options
        ]
        later_default = len(options) - 1
        if compare.startswith("Visits") and len(options) > 1:
            # The later visit with the most frames has the least noise
            later_default = 1 + int(np.argmax([f["n_frames"] for f in options[1:]]))
        diff_col, explain_col = st.columns(2, gap="large")
        with explain_col:
            a = st.selectbox("Earlier", range(len(options)), index=0, format_func=lambda k: labels[k])
            b = st.selectbox("Later", range(len(options)), index=later_default,
                             format_func=lambda k: labels[k])
            st.markdown(
                "Later minus earlier. What stayed the same turns black. A star that moved leaves "
                "**:blue[blue]** where it was and **:orange[orange]** where it went."
            )
            st.caption(
                "Isolated single-pixel spots are usually cosmic rays. Small brightness differences "
                "can come from wavelength, not real change."
            )
            if options[a].get("telescope") != options[b].get("telescope"):
                st.info("You are comparing two telescopes: the star's position is meaningful, "
                        "but brightness differences are not.")
            if mode == FOLLOW_STAR:
                st.warning("In 'Follow the star' the star is kept centered, so here the background "
                           "stars are what moves. Switch to 'Fixed sky' to see the star's own motion.")
        with diff_col:
            st.image(make_difference_image(options[a], options[b], zoom=zoom))
            st.caption("🟦 **:blue[blue]** = where it was · 🟧 **:orange[orange]** = where it is now · "
                       "black = no change")
