import re

import streamlit as st
from core.content import read_markdown

TAB_ICONS = {"SPHEREx": "🛰️", "Visual magnitude": "✨", "Infrared": "🌡️"}

st.title("Learn")
st.caption("The ideas behind the blink, in three short reads.")

# learn.md: "# Learn", then one "## SECTION" per tab
sections = re.split(r"^## ", read_markdown("learn.md"), flags=re.MULTILINE)[1:]
if not sections:
    st.markdown(read_markdown("learn.md"))
    st.stop()

names = []
for section in sections:
    heading = section.splitlines()[0].replace("*", "").strip()
    names.append("SPHEREx" if heading.upper() == "SPHEREX" else heading.capitalize())

tabs = st.tabs([f"{TAB_ICONS.get(name, '📘')} {name}" for name in names])
for tab, name, section in zip(tabs, names, sections):
    with tab:
        body = section.split("\n", 1)[1] if "\n" in section else ""
        question, _, rest = body.strip().partition("\n")
        if question.startswith("### "):
            st.markdown(question.replace("***", "**"))  # first question as the tab's heading
        else:
            rest = body
        if name == "SPHEREx":
            # Figures quoted from the SPHEREx paragraph of learn.md
            facts = [("Spectral channels", "102", None),
                     ("Wavelength range", "0.75–5 µm", "near-infrared"),
                     ("Coverage", "Whole sky", None)]
            for column, (label, value, note) in zip(st.columns(3), facts):
                with column:
                    with st.container(border=True, height="stretch"):
                        st.caption(label)
                        st.markdown(f"## {value}")
                        if note:
                            st.caption(note)
        st.markdown(rest)
        if name == "SPHEREx":
            st.info("**Key idea:** each SPHEREx frame sees a slightly different wavelength, so some "
                    "brightness changes between frames are color, not real variation.", icon="💡")
