import streamlit as st
from core.animate import make_blink_gif
from core.content import read_markdown
from core.demo import load_frames
from core.targets import TARGETS

st.title("Stories")

tabs = st.tabs([target["label"] for target in TARGETS])
for tab, target in zip(tabs, TARGETS):
    with tab:
        st.markdown(read_markdown("stories/" + target["file_name"] + ".md"))
        frames = load_frames(target["file_name"])
        if len(frames) > 0:
            st.image(make_blink_gif(frames))
            st.caption(f"SPHEREx data, {len(frames)} frames")
