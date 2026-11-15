import streamlit as st
from core.content import read_markdown

# learn.md brings its own "# Learn" title
st.markdown(read_markdown("learn.md"))
