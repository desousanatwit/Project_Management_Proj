import streamlit as st

#
#   UI Layout 
#   todo: Add a side bar with buttons to navigate between differnet pages
#   todo: Pages will include: Home, Schedule, Add Shift, etc
#---------------
st.markdown("<h1 style='text-align: center;'>Scheduling</h1>", unsafe_allow_html=True)
st.markdown("---")
 
left, right = st.columns(2)

with left:
    st.markdown("<h3>Menu</h3>", unsafe_allow_html=True)
with right:
    st.markdown("<h3>Home</h3>", unsafe_allow_html=True)
    