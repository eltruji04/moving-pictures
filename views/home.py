import streamlit as st
from core.animate import make_blink_gif
from core.demo import crop_frames, demo_name, load_frames

HERO_FIELD_DEG = 0.1
HERO_WIDTH_PX = 420

st.title("Moving Pictures")
st.subheader("Catch the sky in motion with NASA's SPHEREx telescope")

left, right = st.columns([3, 2], gap="large")
with left:
    st.markdown(
        "SPHEREx is a NASA space telescope that photographs the whole sky in infrared, "
        "again and again.\n\n"
        "Here you can compare its images of the same spot taken on different dates. "
        "Flip between them quickly (a *blink*) and anything that moves or changes "
        "brightness stands out."
    )
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

st.divider()
st.markdown("#### How it works")
steps = [
    ("1 · Pick a spot", "Choose one of five test objects, or type any sky coordinates."),
    ("2 · Blink the dates", "We line up SPHEREx images from different dates, all with the same brightness scale."),
    ("3 · Spot the change", "Stars that move shift position; variable stars get brighter or fainter."),
]
for column, (title, text) in zip(st.columns(3), steps):
    with column:
        with st.container(border=True):
            st.markdown(f"**{title}**")
            st.caption(text)
