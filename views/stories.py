import re

import streamlit as st
from core.animate import make_blink_gif
from core.demo import crop_frames, demo_name, load_frames
from core.targets import TARGETS
from i18n import read_content, t

STORY_FIELD_DEG = 0.1  # close field: shows the motion best
STORY_WIDTH_PX = 600
MOVERS = {"barnard", "eps_ind_b", "wise_0855"}  # the other two change brightness


def split_story(text):
    """Split a story file into its parts. Missing parts come back empty."""
    title = re.search(r"^# (.+)$", text, flags=re.MULTILINE)
    tagline = re.search(r"^### \*([^*¿].*?)#*\*\s*$", text, flags=re.MULTILINE)
    facts = dict(re.findall(r"^- \*\*(.+?):\*\*\s*(.+)$", text, flags=re.MULTILINE))
    # "### *Did you know?*" in English, "### *¿Sabías que...?*" in Spanish
    parts = re.split(r"^### \*(?:Did you know\?|¿Sabías que\.*\?)\*\s*$", text,
                     maxsplit=1, flags=re.MULTILINE)
    body, did_you_know = parts[0], (parts[1] if len(parts) > 1 else "")
    # Body = everything after the fact list
    body_lines = [line for line in body.splitlines()
                  if not line.startswith(("# ", "### ", "- **"))]
    return {
        "title": title.group(1).replace("**", "") if title else "",
        "tagline": tagline.group(1) if tagline else "",
        "facts": facts,
        "body": "\n".join(body_lines).strip(),
        "did_you_know": did_you_know.strip(),
    }


def open_in_explore(target):
    st.session_state["demo_target"] = target
    st.session_state["source"] = "demo"
    st.switch_page("views/explore.py")


st.title(t("Stories", "Historias"))
st.caption(t("Five objects, five reasons to look twice. Three stars that move, two that change brightness. "
             "(🌌 moves across the sky · ✨ changes brightness)",
             "Cinco objetos, cinco razones para mirar dos veces. Tres estrellas que se mueven y dos que "
             "cambian de brillo. (🌌 se mueve en el cielo · ✨ cambia de brillo)"))

tabs = st.tabs([("🌌 " if target["file_name"] in MOVERS else "✨ ") + target["label"] for target in TARGETS])

for tab, target in zip(tabs, TARGETS):
    with tab:
        moves = target["file_name"] in MOVERS
        story = split_story(read_content("stories/" + target["file_name"] + ".md"))
        text_col, gif_col = st.columns([3, 2], gap="large")
        with text_col:
            st.badge(t("Moves across the sky", "Se mueve en el cielo") if moves
                     else t("Changes brightness", "Cambia de brillo"),
                     icon="🌌" if moves else "✨", color="gray")
            st.markdown(f"# {story['title'] or target['label']}")
            if story["tagline"]:
                st.markdown(f"### *{story['tagline']}*")
            facts = list(story["facts"].items())[:3]  # Type, Distance, Visual magnitude (or Tipo…)
            if facts:
                for column, (name, value) in zip(st.columns(len(facts)), facts):
                    with column:
                        st.caption(name)
                        st.markdown(f"**{value}**")
            st.markdown(story["body"])
            if story["did_you_know"]:
                st.info(f"**{t('Did you know?', '¿Sabías que...?')}** {story['did_you_know']}", icon="💡")
            if st.button(t("Explore it yourself", "Exploralo vos"), icon="🔭", key="explore_" + target["file_name"]):
                open_in_explore(target)
        with gif_col:
            saved = load_frames(demo_name(target["file_name"], track_target=False))
            frames = crop_frames(saved, STORY_FIELD_DEG)
            if len(frames) > 0:
                zoom = max(1, STORY_WIDTH_PX // frames[0]["image"].shape[0])
                st.image(make_blink_gif(frames, zoom=zoom))
                st.caption(t(f"SPHEREx data, {len(frames)} frames · fixed sky, {STORY_FIELD_DEG}° field",
                             f"Datos de SPHEREx, {len(frames)} cuadros · cielo fijo, campo de {STORY_FIELD_DEG}°"))
