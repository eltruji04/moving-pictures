import streamlit as st

st.title("Moving Pictures")

st.markdown(
    "SPHEREx is a NASA space telescope that photographs the whole sky in infrared, again and again.  \n"
    "Here you can compare its images of the same spot taken on different dates.  \n"
    "Flip between them quickly (a *blink*) and anything that moves or changes brightness stands out."
)

left, right = st.columns(2)
with left:
    st.page_link("views/explore.py", label="Explore the sky", icon="🔭")
with right:
    st.page_link("views/stories.py", label="Read the stories", icon="📖")
