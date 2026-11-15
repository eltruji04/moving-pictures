import streamlit as st

# Draft text: team members must check names and roles before submitting
TEAM = [
    ("Santiago", "Interface and web app"),
    ("Lucía", "Research, writing and slides"),
]

st.title("About")
st.caption("Team Sidereus Nuncius · NASA Space Apps Challenge 2026 · Montevideo")
st.markdown("Our name comes from Galileo's 1610 book *Sidereus Nuncius*, \"The Starry Messenger\".")

st.header("The team")
for column, (name, role) in zip(st.columns(3), TEAM):
    with column:
        with st.container(border=True):
            st.markdown(f"#### 🔭 {name}")
            st.caption(role)

st.header("Data sources")
with st.container(border=True):
    st.markdown(
        "- **SPHEREx** — NASA/JPL-Caltech, served by [IRSA](https://irsa.ipac.caltech.edu/). "
        "Infrared cutouts, Apr 2025 – May 2026 (collection `spherex_dr1`).\n"
        "- **WISE / AllWISE** — NASA, served by IRSA. The optional 2010 comparison image (band W2).\n"
        "- **SIMBAD** — CDS, Strasbourg. Positions and proper motions of the demo objects.\n"
        "- **Software** — Astropy, astroquery, reproject, NumPy, SciPy, Pillow and Streamlit."
    )

st.header("Limitations")
with st.container(border=True):
    st.markdown(
        "- **The time span is short.** With ~9 months of SPHEREx data, even Barnard's Star moves "
        "only about one pixel. The difference image and the WISE (2010) image help to see it.\n"
        "- **Every frame is at a different wavelength**, so some brightness changes are color, "
        "not real variation. This matters most for RW Aurigae and R Draconis.\n"
        "- **WISE 0855−0714 is extremely faint** and is not visible in these images.\n"
        "- **Cosmic rays are not masked**: spots in a single frame are usually detector artifacts.\n"
        "- **Proper motion is only known for the five test objects**; other positions are "
        "treated as fixed.\n"
        "- **Live search depends on IRSA**, which is sometimes slow or down. That is why the "
        "demo mode exists.\n"
        "- **It's a hackathon project**, built in one weekend. Not a scientific tool."
    )
