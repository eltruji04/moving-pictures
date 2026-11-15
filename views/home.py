import re

import streamlit as st
from core.animate import make_blink_gif
from core.content import read_markdown
from core.demo import crop_frames, demo_name, load_frames

HERO_FIELD_DEG = 0.1
HERO_WIDTH_PX = 600

# home.md = intro (title, tagline, paragraphs) + a "## How it works" numbered list
intro, _, how_it_works = read_markdown("home.md").partition("## How it works")
paragraphs = [p for p in intro.strip().split("\n\n") if p.strip()]

left, right = st.columns([3, 2], gap="large")
with left:
    # Last paragraph ("Made for curious people…") is shown smaller, as a side note
    st.markdown("\n\n".join(paragraphs[:-1]))
    if len(paragraphs) > 1:
        st.caption(paragraphs[-1])
    if st.button("Explore the sky", icon="🔭", type="primary", width=500):
        st.switch_page("views/explore.py")
    st.page_link("views/stories.py", label="Read the stories", icon="📖")
    st.page_link("views/learn.py", label="How does a blink work?", icon="🎓")
with right:
    saved = load_frames(demo_name("barnard", track_target=False))
    frames = crop_frames(saved, HERO_FIELD_DEG)
    if len(frames) > 0:
        zoom = max(1, HERO_WIDTH_PX // frames[0]["image"].shape[0])
        st.image(make_blink_gif(frames, zoom=zoom))
        first = min(f["date"] for f in frames)
        last = max(f["date"] for f in frames)
        st.caption(f"Barnard's Star in SPHEREx images, {first:%b %Y} – {last:%b %Y} (saved demo data).")

# Each step looks like "1. Pick a spot. Type sky coordinates…": number, short title, text
steps = re.findall(r"^\s*(\d+)\.\s*([^.]+)\.\s*(.+)$", how_it_works, flags=re.MULTILINE)
if steps:
    st.divider()
    st.header("How it works")
    for column, (number, title, text) in zip(st.columns(len(steps)), steps):
        with column:
            with st.container(border=True, height="stretch"):
                st.badge(number, color="orange")
                st.markdown(f"#### {title}")
                st.markdown(text)
    st.caption("Heads-up: in 9 months a nearby star moves only about one pixel. "
               "Look closely — that tiny jump is the real signal.")
