import re

import streamlit as st
from core.animate import make_blink_gif
from core.content import read_markdown
from core.demo import crop_frames, demo_name, load_frames
from core.targets import TARGETS

STORY_FIELD_DEG = 0.1  # close field: shows the motion best
STORY_WIDTH_PX = 600
MOVERS = {"barnard", "eps_ind_b", "wise_0855"}  # the other two change brightness
FACT_NAMES = ["Type", "Distance", "Visual magnitude"]


def split_story(text):
    """Split a story file into its parts. Missing parts come back empty."""
    title = re.search(r"^# (.+)$", text, flags=re.MULTILINE)
    tagline = re.search(r"^### \*([^*].*?)\*\s*$", text, flags=re.MULTILINE)
    facts = dict(re.findall(r"^- \*\*(.+?):\*\*\s*(.+)$", text, flags=re.MULTILINE))
    body, _, did_you_know = text.partition("### *Did you know?*")
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


st.title("Stories")
st.caption("Five objects, five reasons to look twice. Three stars that move, two that change brightness. "
           "(🏃 moves across the sky · ✨ changes brightness)")

tabs = st.tabs([("🏃 " if t["file_name"] in MOVERS else "✨ ") + t["label"] for t in TARGETS])

for tab, target in zip(tabs, TARGETS):
    with tab:
        moves = target["file_name"] in MOVERS
        story = split_story(read_markdown("stories/" + target["file_name"] + ".md"))
        text_col, gif_col = st.columns([3, 2], gap="large")
        with text_col:
            st.badge("Moves across the sky" if moves else "Changes brightness",
                     icon="🏃" if moves else "✨", color="gray")
            st.markdown(f"# {story['title'] or target['label']}")
            if story["tagline"]:
                st.markdown(f"### *{story['tagline']}*")
            facts = [(name, story["facts"][name]) for name in FACT_NAMES if name in story["facts"]]
            if facts:
                for column, (name, value) in zip(st.columns(len(facts)), facts):
                    with column:
                        st.caption(name)
                        st.markdown(f"**{value}**")
            st.markdown(story["body"])
            if story["did_you_know"]:
                st.info(f"**Did you know?** {story['did_you_know']}", icon="💡")
            if st.button("Explore it yourself", icon="🔭", key="explore_" + target["file_name"]):
                open_in_explore(target)
        with gif_col:
            saved = load_frames(demo_name(target["file_name"], track_target=False))
            frames = crop_frames(saved, STORY_FIELD_DEG)
            if len(frames) > 0:
                zoom = max(1, STORY_WIDTH_PX // frames[0]["image"].shape[0])
                st.image(make_blink_gif(frames, zoom=zoom))
                st.caption(f"SPHEREx data, {len(frames)} frames · fixed sky, {STORY_FIELD_DEG}° field")
