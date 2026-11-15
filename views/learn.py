import streamlit as st
from core.content import read_markdown

st.title("Learn")
st.caption("SPHEREx, infrared light, and how a blink reveals what moves.")

st.markdown(read_markdown("learn.md"))
