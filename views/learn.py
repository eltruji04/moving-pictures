import re

import streamlit as st
from i18n import read_content, t

TAB_ICONS = ["🛰️", "✨", "🌡️"]  # in the order of the sections in learn.md

st.title(t("Learn", "Aprender"))
st.caption(t("The ideas behind the blink, in three short reads.",
             "Las ideas detrás del blink, en tres lecturas cortas."))

# learn.md: "# Learn", then one "## SECTION" per tab
sections = re.split(r"^## ", read_content("learn.md"), flags=re.MULTILINE)[1:]
if not sections:
    st.markdown(read_content("learn.md"))
    st.stop()

names = []
for section in sections:
    heading = section.splitlines()[0].replace("*", "").strip()
    names.append("SPHEREx" if heading.upper() == "SPHEREX" else heading.capitalize())

icons = TAB_ICONS + ["📘"] * len(names)
tabs = st.tabs([f"{icon} {name}" for icon, name in zip(icons, names)])
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
            facts = [(t("Spectral channels", "Canales espectrales"), "102", None),
                     (t("Wavelength range", "Rango de longitud de onda"), "0.75–5 µm",
                      t("near-infrared", "infrarrojo cercano")),
                     (t("Coverage", "Cobertura"), t("Whole sky", "Todo el cielo"), None)]
            for column, (label, value, note) in zip(st.columns(3), facts):
                with column:
                    with st.container(border=True, height="stretch"):
                        st.caption(label)
                        st.markdown(f"## {value}")
                        if note:
                            st.caption(note)
        st.markdown(rest)
        if name == "SPHEREx":
            st.info(t("**Key idea:** each SPHEREx frame sees a slightly different wavelength, so some "
                      "brightness changes between frames are color, not real variation.",
                      "**Idea clave:** cada cuadro de SPHEREx ve una longitud de onda un poco distinta, así que "
                      "algunos cambios de brillo entre cuadros son color, no variación real."), icon="💡")
