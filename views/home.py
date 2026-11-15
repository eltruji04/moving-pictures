import streamlit as st
from core.animate import make_blink_gif
from core.content import read_markdown
from core.demo import crop_frames, demo_name, load_frames

HERO_FIELD_DEG = 0.1
HERO_WIDTH_PX = 420

# home.md = intro (with its own title) + a "## How it works" section shown below the hero
intro, heading, how_it_works = read_markdown("home.md").partition("## How it works")

left, right = st.columns([3, 2], gap="large")
with left:
    st.markdown(intro)
    st.page_link("views/explore.py", label="Explore the sky", icon="🔭", width="stretch")
    st.page_link("views/stories.py", label="Read the stories", icon="📖", width="stretch")
    st.page_link("views/learn.py", label="How does a blink work?", icon="🎓", width="stretch")
with right:
    saved = load_frames(demo_name("barnard", track_target=False))
    frames = crop_frames(saved, HERO_FIELD_DEG)
    if len(frames) > 0:
        zoom = max(1, HERO_WIDTH_PX // frames[0]["image"].shape[0])
        st.image(make_blink_gif(frames, zoom=zoom))
        first = min(f["date"] for f in frames)
        last = max(f["date"] for f in frames)
        st.caption(f"Barnard's Star in SPHEREx images, {first:%b %Y} – {last:%b %Y} (saved demo data).")

if heading:
    st.divider()
    with st.container(border=True):
        st.markdown(heading + how_it_works)
