import streamlit as st
from core.content import read_markdown

st.title("About")

st.markdown(read_markdown("about.md"))
