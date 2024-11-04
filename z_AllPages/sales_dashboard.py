import streamlit as st

# Style to reduce header height
reduce_header_height_style = """
    <style>
        div.block-container {padding-top:1rem;}
    </style>
"""
st.markdown(reduce_header_height_style, unsafe_allow_html=True)

# --------TABS FOR DIFFERENT DASHBOARDS--------------------------


# Create tabs for different forms
tab = st.tabs(["Dashboard1", "Dashboard2", "Dashboard3"])

# Route Planner Form Tab
with tab[0]:
    st.subheader("Some content here")

with tab[1]:
    st.subheader("Some content here")

with tab[2]:
    st.subheader("Some content here")
