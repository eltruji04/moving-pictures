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

# Language for Home, Stories and Learn (see i18n.py); shown at the top right of every page
_, lang_col = st.columns([8, 1])
with lang_col:
    st.segmented_control("Language", ["EN", "ES"], default="EN", required=True,
                         key="lang", label_visibility="collapsed")

nav.run()
