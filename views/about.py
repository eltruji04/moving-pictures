import streamlit as st
from core.content import read_markdown

st.title("About")
st.caption("Team Sidereus Nuncius · NASA Space Apps Challenge 2026 · Montevideo")

text = read_markdown("about.md")
if text.strip():
    st.markdown(text)
else:
    st.info("Team, sources, limitations and use of AI: coming soon.")
