"""Language switch (EN/ES) for the content pages. Explore and About stay in English."""
import streamlit as st
from core.content import read_markdown

PLACEHOLDER = read_markdown("__missing__.md")  # what read_markdown returns for a missing file

# English file in content/ -> Spanish file in contentEs/
ES_FILES = {
    "home.md": "inicio.md",
    "learn.md": "aprender.md",
    "stories/barnard.md": "historias/barnardsstar.md",
    "stories/eps_ind_b.md": "historias/epsilonindib.md",
    "stories/wise_0855.md": "historias/wise0855−0714.md",  # the name uses a minus sign (−), not a hyphen
    "stories/rw_aur.md": "historias/rwaurigae.md",
    "stories/r_dra.md": "historias/rdraconis.md",
}


def is_spanish():
    return st.session_state.get("lang") == "ES"


def t(english, spanish):
    """Pick the interface text for the current language."""
    return spanish if is_spanish() else english


def read_content(name):
    """Read a content file in the current language; fall back to English if there's no translation."""
    if is_spanish() and name in ES_FILES:
        text = read_markdown("../contentEs/" + ES_FILES[name])
        if text.strip() and text != PLACEHOLDER:
            return text
    return read_markdown(name)
