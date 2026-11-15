import re

import streamlit as st
from core.animate import make_blink_gif
from core.demo import crop_frames, demo_name, load_frames
from i18n import read_content, t

HERO_FIELD_DEG = 0.1
HERO_WIDTH_PX = 600

# home.md = intro (title, tagline, paragraphs) + one "## …" section with a numbered list
intro, _, how_it_works = read_content("home.md").partition("\n## ")
steps_heading, _, how_it_works = how_it_works.partition("\n")
paragraphs = [p for p in intro.strip().split("\n\n") if p.strip()]

left, right = st.columns([3, 2], gap="large")
with left:
    # Last paragraph ("Made for curious people…") is shown smaller, as a side note
    st.markdown("\n\n".join(paragraphs[:-1]))
    if len(paragraphs) > 1:
        st.caption(paragraphs[-1])
    if st.button(t("Explore the sky", "Explorá el cielo"), icon="🔭", type="primary", width=500):
        st.switch_page("views/explore.py")
    st.page_link("views/stories.py", label=t("Read the stories", "Leé las historias"), icon="📖")
    st.page_link("views/learn.py", label=t("How does a blink work?", "¿Cómo funciona un blink?"), icon="🎓")
with right:
    saved = load_frames(demo_name("barnard", track_target=False))
    frames = crop_frames(saved, HERO_FIELD_DEG)
    if len(frames) > 0:
        zoom = max(1, HERO_WIDTH_PX // frames[0]["image"].shape[0])
        st.image(make_blink_gif(frames, zoom=zoom))
        first = min(f["date"] for f in frames)
        last = max(f["date"] for f in frames)
        st.caption(t(f"Barnard's Star in SPHEREx images, {first:%m/%Y} – {last:%m/%Y} (saved demo data).",
                     f"La estrella de Barnard en imágenes de SPHEREx, {first:%m/%Y} – {last:%m/%Y} (datos guardados de la demo)."))

# Each step looks like "1. Pick a spot. Type sky coordinates…": number, short title, text
steps = re.findall(r"^\s*(\d+)\.\s*([^.]+)\.\s*(.+)$", how_it_works, flags=re.MULTILINE)
if steps:
    st.divider()
    st.header(steps_heading.replace("*", "").strip())
    for column, (number, title, text) in zip(st.columns(len(steps)), steps):
        with column:
            with st.container(border=True, height="stretch"):
                st.badge(number, color="orange")
                st.markdown(f"#### {title}")
                st.markdown(text)
    st.caption(t("Heads-up: in 9 months a nearby star moves only about one pixel. "
                 "Look closely — that tiny jump is the real signal.",
                 "Ojo: en 9 meses una estrella cercana se mueve apenas un píxel. "
                 "Mirá con atención: ese saltito es la señal real."))
