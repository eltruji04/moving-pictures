import streamlit as st
from core.animate import make_blink_gif
from core.content import read_markdown
from core.demo import crop_frames, demo_name, load_frames
from core.targets import TARGETS

STORY_FIELD_DEG = 0.1  # close field: shows the motion best
STORY_WIDTH_PX = 600

st.title("Stories")

tabs = st.tabs([target["label"] for target in TARGETS])
for tab, target in zip(tabs, TARGETS):
    with tab:
        st.markdown(read_markdown("stories/" + target["file_name"] + ".md"))
        saved = load_frames(demo_name(target["file_name"], track_target=False))
        frames = crop_frames(saved, STORY_FIELD_DEG)
        if len(frames) > 0:
            zoom = max(1, STORY_WIDTH_PX // frames[0]["image"].shape[0])
            st.image(make_blink_gif(frames, zoom=zoom))
            st.caption(f"SPHEREx data, {len(frames)} frames")
