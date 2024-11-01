import os
import streamlit as st
from streamlit_gsheets import GSheetsConnection
from Aforms.newrouterform import route_planner
from Aforms.dailyform import daily_form
from Aforms.hcpform import hcp_form


# Load custom CSS
def load_custom_css():
    with open("assets/css/style.css", "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


# create a connection to the Google Sheet
conn = st.connection("gsheets", type=GSheetsConnection)


@st.cache_data(ttl=300)
def load_route_data():
    return conn.read(worksheet="RoutePlanner")


@st.cache_data(ttl=300)
def load_daily_data():
    return conn.read(worksheet="DailyData")


@st.cache_data(ttl=300)
def load_hcp_data():
    return conn.read(worksheet="HCPData")


def show_forms_page():
    # Load the CSS at the beginning of the page
    load_custom_css()

    # Create tabs for different forms
    tab = st.tabs(["Route Planner Form", "Daily Reporting Form", "HCP Form"])

    # Route Planner Form Tab
    with tab[0]:
        # Define button container with a unique key
        with st.container(key="route_buttons_container"):
            col1, col2 = st.columns(2, gap="small")

            with col1:
                # Expander for Action
                with st.expander(
                    "Action", expanded=False, icon=":material/ads_click:"
                ):  # Set expanded=True if you want it open by default
                    col1, col2, col3 = st.columns(3, gap="small")
                    with col1:

                        @st.dialog("Route Planner Form")
                        def show_route_form():
                            route_planner()

                        if st.button(
                            "Add",
                            help="Click to add route plan",
                            type="primary",
                            icon=":material/library_add:",
                            key="add_route_plan_button",
                        ):
                            show_route_form()

                    with col2:

                        # Button to clear cache
                        if st.button(
                            "Refresh",
                            help="Click to Refresh Data",
                            type="secondary",
                            icon=":material/refresh:",
                            key="refresh_route_planner",
                        ):
                            st.cache_data.clear()  # Clear the cache
                            st.toast("Cache cleared. Reloading data...", icon="✅")

                    with col3:
                        st.button(
                            "Filters",
                            help="Click to add filters",
                            type="secondary",
                            icon=":material/library_add:",
                            key="route_filter_button",
                        )

        # Google Sheets connection and data display
        Route_data = load_route_data()
        if Route_data.empty:
            col1, col2, col3 = st.columns(3, gap="small")
            with col2:
                st.image(
                    "assets/images/alert.png",
                    caption="Alert: No data available. Please add a route plan to the spreadsheet.",
                )
        else:
            st.dataframe(Route_data)

    # Daily Reporting Form Tab
    with tab[1]:
        # st.markdown("### Daily Activity Details")
        # st.write("Please fill out the Form below:")

        with st.container(key="daily_buttons_container"):
            col1, col2 = st.columns(2, gap="small")

            with col1:
                # Expander for Action
                with st.expander("Action", expanded=False, icon=":material/ads_click:"):
                    col1, col2, col3 = st.columns(3, gap="small")
                    with col1:

                        @st.dialog("Daily Activity Form")
                        def show_daily_form():
                            daily_form()

                        if st.button(
                            "Add ",
                            help="Click to add activity",
                            type="primary",
                            icon=":material/library_add:",
                            key="add_daily_form_button",
                        ):

                            show_daily_form()

                    with col2:
                        # Button to clear cache
                        if st.button(
                            "Refresh",
                            help="Click to Refresh Data",
                            type="secondary",
                            icon=":material/refresh:",
                            key="more_daily_form",
                        ):
                            st.cache_data.clear()  # Clear the cache
                            st.toast("Cache cleared. Reloading data...", icon="✅")
                    with col3:

                        st.button(
                            "Filters",
                            help="Click to filter data",
                            type="secondary",
                            icon=":material/library_add:",
                            key="filter_daily_form_button",
                        )

        # Google Sheets connection and data display
        # Use the function to get the data
        Daily_data = load_daily_data()
        if Daily_data.empty:
            col1, col2, col3 = st.columns(3, gap="small")
            with col2:
                st.image(
                    "assets/images/alert.png",
                    caption="Alert: No data available. Please add to view.",
                )
        else:
            st.dataframe(Daily_data)

    # HCP Form Tab
    with tab[2]:
        # st.markdown("### HCP Form")
        # st.write("Please fill out the HCP Form below:")

        # establishing a Google Sheets connection
        with st.container(key="hcp_buttons_container"):
            col1, col2 = st.columns(2, gap="small")

            with col1:
                # Expander for Action
                with st.expander("Action", expanded=False, icon=":material/ads_click:"):
                    col1, col2, col3 = st.columns(3, gap="small")
                    with col1:

                        @st.dialog("HCP Form")
                        def show_hcp_form():
                            hcp_form()

                        if st.button(
                            "Add",
                            help="Click to add HCP",
                            type="primary",
                            icon=":material/library_add:",
                            key="add_hcp_form_button",
                        ):
                            show_hcp_form()

                    with col2:
                        # Button to clear cache
                        if st.button(
                            "Refresh",
                            help="Click to Refresh Data",
                            type="secondary",
                            icon=":material/refresh:",
                            key="more_hcp_form",
                        ):
                            st.cache_data.clear()  # Clear the cache
                            st.toast("Cache cleared. Reloading data...", icon="✅")

                    with col3:
                        st.button(
                            "Filters",
                            help="Click to add filters",
                            type="secondary",
                            icon=":material/library_add:",
                            key="filter_hcp_form_button",
                        )

        # Google Sheets connection and data display
        HCP_data = load_hcp_data()
        if HCP_data.empty:
            col1, col2, col3 = st.columns(3, gap="small")
            with col2:
                st.image(
                    "assets/images/alert.png",
                    caption="Alert: No data available. Please add to view.",
                )
        else:
            st.dataframe(HCP_data)


# with tab[3]:
#     # Daily Report Form
#     st.markdown("### Daily Reporting Form")
#     st.write("Please fill out the Daily Reporting Form below:")
#     daily_report_form_url = "https://forms.office.com/Pages/ResponsePage.aspx?id=DQSIkWdsW0yxEjajBLZtrQAAAAAAAAAAAANAAf9rZzVUM1czODc3UUtCVlNYT00wTUVVTFZMNEc5SC4u"
#     embed_daily_report_form(daily_report_form_url)

# with tab[2]:
#     # HCP Form
#     st.markdown("### HCP Form")
#     hcp_form_url = "https://forms.office.com/Pages/ResponsePage.aspx?id=DQSIkWdsW0yxEjajBLZtrQAAAAAAAAAAAANAAf9rZzVUQ0VINTBGNlRDN1dRRDJHSTdLTjVYMUZKUC4u"
#     embed_hcp_form(hcp_form_url)


# def embed_daily_report_form(url):
#     iframe_html = f"""
#     <iframe src="{url}" width="100%" height="600" frameborder="0" marginheight="0" marginwidth="0">
#     Loading…
#     </iframe>
#     """
#     st.components.v1.html(iframe_html, height=600)


# def embed_hcp_form(url):
#     iframe_html = f"""
#     <iframe src="{url}" width="100%" height="600" frameborder="0" marginheight="0" marginwidth="0">
#     Loading…
#     </iframe>
#     """
#     st.components.v1.html(iframe_html, height=600)
