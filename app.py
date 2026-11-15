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
nav.run()
