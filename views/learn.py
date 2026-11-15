import streamlit as st
from core.content import read_markdown

st.title("Learn")

st.markdown(read_markdown("learn.md"))
