import streamlit as st

st.set_page_config(
    page_title="Moving pictures",
    page_icon="🔭",
    layout="wide",
)

pages = [
    st.Page("views/home.py", title="Home", icon="🏠", default=True),
    st.Page("views/explore.py", title="Explore", icon="🔭"),
    st.Page("views/stories.py", title="Stories", icon="📖"),
    st.Page("views/learn.py", title="Learn", icon="🎓"),
    st.Page("views/about.py", title="About", icon="ℹ️"),
]
nav = st.navigation(pages, position="top")

TRANSLATED_PAGES = {"Home", "Stories", "Learn"}  # Explore and About are English only


def _save_language():
    # The switch is hidden on some pages, and Streamlit forgets a hidden widget's value,
    # so the chosen language is kept in "lang" (read by i18n.py) instead
    st.session_state["lang"] = st.session_state["lang_switch"]


# Language switch at the top right, only on the pages that have a Spanish version
if nav.title in TRANSLATED_PAGES:
    _, lang_col = st.columns([8, 1])
    with lang_col:
        st.segmented_control("Language", ["EN", "ES"], default=st.session_state.get("lang", "EN"),
                             required=True, key="lang_switch", on_change=_save_language,
                             label_visibility="collapsed")

nav.run()
