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

    import streamlit as st

    def clear_text():
        st.session_state.my_text = st.session_state.widget
        st.session_state.widget = ""

    st.text_input("Enter text here:", key="widget", on_change=clear_text)
    my_text = st.session_state.get("my_text", "")
    #                          ^^^   <--- here
    st.write(my_text)


with tab[1]:
    st.subheader("Some content here")

with tab[2]:
    st.subheader("Some content here")
