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
        existing_route_data = conn.read(worksheet="RoutePlanner")
        settings_list_data = conn.read(worksheet="Settings")

        # List of data imports from sheets
        TERRITORIES = settings_list_data["Territories"].unique().tolist()
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

        AGENTNAMES = settings_list_data["Names"].unique().tolist()
        REGIONS = settings_list_data["Regions"].unique().tolist()
        INSTITUTIONS = settings_list_data["Institutions"].unique().tolist()

        # Onboarding New Route Plan Form
        with st.form(key="route_planner_form"):
            territories = st.selectbox("Territory*", options=TERRITORIES, index=None)
            month = st.selectbox("Month*", options=MONTHS, index=None)
            week = st.selectbox("Week*", options=WEEKS, index=None)
            day = st.selectbox("Day*", options=DAYS, index=None)
            date = st.date_input(label="Route Plan Date")
            agentname = st.selectbox("Your Name*", options=AGENTNAMES, index=None)
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
                    or not date
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
                    updated_route_df = pd.concat(
                        [existing_route_data, route_data], ignore_index=True
                    )

                    # Update Google Sheets with the new Route Plan data
                    conn.update(worksheet="RoutePlanner", data=updated_route_df)

                    st.success(
                        icon=":material/thumb_up:",
                        body="Route Plan details successfully submitted!",
                    )

    with tab[1]:
        # Route Planner Form
        st.markdown("### Daily Activity Details")
        st.write("Please fill out the Form below:")

        # Fetch existing RoutePlanner data
        existing_daily_data = conn.read(worksheet="DailyData")

        # List of data imports from sheets
        PREFIXES = settings_list_data["Prefixes"].unique().tolist()
        CADRE = settings_list_data["Cadre"].unique().tolist()
        TYPE = settings_list_data["Type"].unique().tolist()
        DEPARTMENT = settings_list_data["Department"].unique().tolist()

        COLORCODES = settings_list_data["Colour_CODE"].unique().tolist()
        GOALS = settings_list_data["Cycle_Goals"].unique().tolist()
        PRODUCTS = settings_list_data["Products"].unique().tolist()

        # Onboarding New Daily Activity Form
        with st.form(key="daily_form"):
            agentname = st.selectbox("Your Name*", options=AGENTNAMES, index=None)
            territories = st.selectbox("Territory*", options=TERRITORIES, index=None)
            date = st.date_input(label="Date")
            prefix = st.selectbox("prefix*", options=PREFIXES, index=None)
            client_surname = st.text_input(label="HCP/Client Surname*")
            client_firstname = st.text_input(label="HCP/Client Firstname*")
            cadre = st.selectbox("Cadre*", options=CADRE, index=None)
            pos_type = st.selectbox("Institution (POS) Type*", options=TYPE, index=None)
            department = st.selectbox(
                "Institution Department*", options=DEPARTMENT, index=None
            )
            objective = st.text_input(label="Task Objective*")
            comments = st.text_area(label="Comments/Notes*")
            future_objective = st.text_area(label="Future Task Objective")
            appointment = st.date_input(label="Next Appointment")

            # Mark mandatory fields
            st.markdown("**required*")

            submit_button = st.form_submit_button(
                label="Submit your Details",
                help="Submit your Details",
                type="primary",
                icon=":material/send_money:",
                # use_container_width=True,
            )

            # If the submit button is pressed
            if submit_button:
                # Check if all mandatory fields are filled
                if (
                    not territories
                    or not date
                    or not agentname
                    or not prefix
                    or not client_surname
                    or not client_firstname
                    or not cadre
                    or not pos_type
                    or not department
                    or not objective
                    or not comments
                    or not future_objective
                    or not appointment
                ):
                    st.warning(
                        icon=":material/error:",
                        body="Ensure all fields are filled.",
                    )
                    st.stop()
                # elif
                else:
                    # Create a new row of Route Plan data
                    daily_data = pd.DataFrame(
                        [
                            {
                                "Name": territories,
                                "Territory": territories,
                                "Date": date.strftime("%Y-%m-%d"),
                                "Prefix": prefix,
                                "HCP_Surname": client_surname,
                                "HCP_Firstname": client_firstname,
                                "Cadre": cadre,
                                "Institution_(POS)_Type": pos_type,
                                "Institution_Department": department,
                                "Task_Objective": objective,
                                "Comments/Notes": comments,
                                "Future_Task_Objective": future_objective,
                                "Next_Appointment": appointment.strftime("%Y-%m-%d"),
                            }
                        ]
                    )

                    # Add the new Route Plan data to the existing data
                    updated_daily_df = pd.concat(
                        [existing_daily_data, daily_data], ignore_index=True
                    )

                    # Update Google Sheets with the new Route Plan data
                    conn.update(worksheet="DailyData", data=updated_daily_df)

                    st.success(
                        icon=":material/thumb_up:",
                        body="Route Plan details successfully submitted!",
                    )

    # with tab[3]:
    #     # Daily Report Form
    #     st.markdown("### Daily Reporting Form")
    #     st.write("Please fill out the Daily Reporting Form below:")
    #     daily_report_form_url = "https://forms.office.com/Pages/ResponsePage.aspx?id=DQSIkWdsW0yxEjajBLZtrQAAAAAAAAAAAANAAf9rZzVUM1czODc3UUtCVlNYT00wTUVVTFZMNEc5SC4u"
    #     embed_daily_report_form(daily_report_form_url)

    with tab[2]:
        # HCP Form
        st.markdown("### HCP Form")
        hcp_form_url = "https://forms.office.com/Pages/ResponsePage.aspx?id=DQSIkWdsW0yxEjajBLZtrQAAAAAAAAAAAANAAf9rZzVUQ0VINTBGNlRDN1dRRDJHSTdLTjVYMUZKUC4u"
        embed_hcp_form(hcp_form_url)


# def embed_daily_report_form(url):
#     iframe_html = f"""
#     <iframe src="{url}" width="100%" height="600" frameborder="0" marginheight="0" marginwidth="0">
#     Loading…
#     </iframe>
#     """
#     st.components.v1.html(iframe_html, height=600)


def embed_hcp_form(url):
    iframe_html = f"""
    <iframe src="{url}" width="100%" height="600" frameborder="0" marginheight="0" marginwidth="0">
    Loading…
    </iframe>
    """
    st.components.v1.html(iframe_html, height=600)
