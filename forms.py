import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd


def show_forms_page():
    # st.markdown(
    #     """
    # <style>
    # .stTabs [data-baseweb="tab-list"] {
    # 	gap: 5px;
    # }
    # .stTabs [data-baseweb="tab"] {
    #     white-space: pre-wrap;
    # 	background-color: transparent;
    # 	border-radius: 10px 10px 0px 0px;
    #     border-right: 1px solid #f0daf2;
    #     padding-left: 10px;
    #     padding-right: 10px;
    # }
    # .stTabs [aria-selected="true"] {
    # 	background-color: #f0daf2;
    #     color: #000;
    #     font-weight: bold;
    # }
    # </style>""",
    #     unsafe_allow_html=True,
    # )


    # Create tabs for different forms
    tab = st.tabs(["Route Planner Form", "Daily Reporting Form", "HCP Form"])

    with tab[0]:
        # Route Planner Form
        st.markdown("### Route Planner Form")
        st.write("Please fill out the Route Planner Form below:")

        # Establishing a Google Sheets connection
        conn = st.connection("gsheets", type=GSheetsConnection)

        # Fetch existing RoutePlanner data
        existing_data = conn.read(worksheet="RoutePlanner")
        route_list_data = conn.read(worksheet="Institutions")

        # List of Business Types and Products
        TERRITORIES = route_list_data["Territories"].unique().tolist()
        MONTHS = [
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December",
        ]
        WEEKS = [1, 2, 3, 4, 5]
        DAYS = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]

        AGENTNAMES = route_list_data["Names"].unique().tolist()
        REGIONS = route_list_data["Regions"].unique().tolist()
        INSTITUTIONS = route_list_data["Institutions"].unique().tolist()

        # Onboarding New Route Plan Form
        with st.form(key="route_planner_form"):
            territories = st.selectbox("Territory*", options=TERRITORIES, index=None)
            month = st.selectbox("Month*", options=MONTHS, index=None)
            week = st.selectbox("Week*", options=WEEKS, index=None)
            day = st.selectbox("Day*", options=DAYS, index=None)
            date = st.date_input(label="Route Plan Date")
            agentname = st.selectbox("Agent Name*", options=AGENTNAMES, index=None)
            region = st.selectbox("Region*", options=REGIONS, index=None)
            institutions = st.multiselect("Institutions / Stores", options=INSTITUTIONS)

            # Mark mandatory fields
            st.markdown("**required*")

            submit_button = st.form_submit_button(
                label="Submit Route Plan",
                help="Submit Route Plan",
                type="primary",
                icon=":material/send_money:",
                # use_container_width=True,
            )

            # If the submit button is pressed
            if submit_button:
                # Check if all mandatory fields are filled
                if (
                    not territories
                    or not month
                    or not week
                    or not day
                    or not agentname
                    or not region
                    or not institutions
                ):
                    st.warning(
                        icon=":material/error:",
                        body="Ensure all mandatory fields are filled.",
                    )
                    st.stop()
                else:
                    # Create a new row of Route Plan data
                    route_data = pd.DataFrame(
                        [
                            {
                                "Territory": territories,
                                "Month": month,
                                "Week": week,
                                "Day": day,
                                "Date": date.strftime("%Y-%m-%d"),
                                "Agent": agentname,
                                "Region": region,
                                "Institutions": ", ".join(institutions),
                            }
                        ]
                    )

                    # Add the new Route Plan data to the existing data
                    updated_df = pd.concat(
                        [existing_data, route_data], ignore_index=True
                    )

                    # Update Google Sheets with the new Route Plan data
                    conn.update(worksheet="RoutePlanner", data=updated_df)

                    st.success(
                        icon=":material/thumb_up:",
                        body="Route Plan details successfully submitted!",
                    )

    with tab[1]:
        # Daily Report Form
        st.markdown("### Daily Reporting Form")
        st.write("Please fill out the Daily Reporting Form below:")
        daily_report_form_url = "https://forms.office.com/Pages/ResponsePage.aspx?id=DQSIkWdsW0yxEjajBLZtrQAAAAAAAAAAAANAAf9rZzVUM1czODc3UUtCVlNYT00wTUVVTFZMNEc5SC4u"
        embed_daily_report_form(daily_report_form_url)

    with tab[2]:
        # HCP Form
        st.markdown("### HCP Form")
        hcp_form_url = "https://forms.office.com/Pages/ResponsePage.aspx?id=DQSIkWdsW0yxEjajBLZtrQAAAAAAAAAAAANAAf9rZzVUQ0VINTBGNlRDN1dRRDJHSTdLTjVYMUZKUC4u"
        embed_hcp_form(hcp_form_url)


def embed_daily_report_form(url):
    iframe_html = f"""
    <iframe src="{url}" width="100%" height="600" frameborder="0" marginheight="0" marginwidth="0">
    Loading…
    </iframe>
    """
    st.components.v1.html(iframe_html, height=600)


def embed_hcp_form(url):
    iframe_html = f"""
    <iframe src="{url}" width="100%" height="600" frameborder="0" marginheight="0" marginwidth="0">
    Loading…
    </iframe>
    """
    st.components.v1.html(iframe_html, height=600)
