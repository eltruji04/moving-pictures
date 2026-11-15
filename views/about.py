import streamlit as st
from core.content import read_markdown

st.title("About")
st.caption("Team Sidereus Nuncius · NASA Space Apps Challenge 2026 · Montevideo")

st.markdown(read_markdown("about.md"))
