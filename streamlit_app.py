import time
import pandas as pd
import math
from datetime import datetime
import streamlit as st
import streamlit_shadcn_ui as ui
import streamlit_antd_components as sac
import streamlit_authenticator as stauth
from streamlit_gsheets import GSheetsConnection

# --------------------SETUP THE STREAMLIT PAGE CONFIGURATION---------------------------------------------------------------
st.set_page_config(
    page_title="AlphaPlus",
    page_icon=":material/home:",
    initial_sidebar_state="collapsed",
    layout="wide",
)
# --------------------REDUCE HEADER HEIGHT---------------------------------------------------------------
reduce_header_height_style = """
    <style>
        div.block-container {padding-top:1rem;}
    </style>
"""
st.markdown(reduce_header_height_style, unsafe_allow_html=True)

# --------------------CUSTOM CSS TO REMOVE PADDING---------------------------------------------------------------
st.markdown(
    """
            <style>
            .st-emotion-cache-1jicfl2 {
    width: 100%;
    padding: 6rem 1rem 10rem;
    min-width: auto;
    max-width: initial;
}
            """,
    unsafe_allow_html=True,
)

# --------------------LOAD USER DATA FROM GOOGLE SHEETS---------------------------------------------------------------
from data import credentials

# --------------------SETUP THE STREAMLIT AUTHENTICATOR---------------------------------------------------------------
Authenticator = stauth.Authenticate(
    credentials,
    cookie_name="alphaplus",
    key="AUTH_SECRET_KEY",
    cookie_expiry_days=30,
)

# --------------------LOGIN FORM---------------------------------------------------------------
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    try:
        with st.spinner("    Fetching ..."):
            name_or_status = Authenticator.login(
                fields={
                    "Form name": "Login to Alpa + ",
                    "Login": "Get Access",
                },
                location="main",
            )
            if st.session_state.get("authentication_status"):
                time.sleep(2)  # Short delay for smooth transition
    except Exception as e:
        st.error(e)

# --------------------AUTHENTICATION CHECK---------------------------------------------------------------
if st.session_state["authentication_status"]:
    st.session_state["credentials"] = credentials
    st.session_state["authenticated"] = True
    st.session_state["username"] = st.session_state["username"]
    st.session_state["name"] = st.session_state["name"]
    st.session_state["user_credentials"] = credentials["usernames"][
        st.session_state["username"]
    ]

    # --- SHARED ON ALL AllPages ---------------------------------------------------------------------------------
    st.logo("static/logo.png", size="large")
    # ---- Display content after login ---------------------------------------------------------------
    primary_color = st.get_option("theme.primaryColor")
    username = st.session_state["username"]
    user_credentials = credentials["usernames"][username]
    user_role = user_credentials["role"]
    # --------------------GET USER SPECIFIC DATA(Signed in user)---------------------------------------------------------------
    username = st.session_state["username"]
    user_credentials = st.session_state["user_credentials"]
    user_territory = user_credentials["Territory_ID"]

    # --------------------CUSTOM CSS---------------------------------------------------------------
    def load_custom_css():
        with open("assets/css/style.css", "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    load_custom_css()

    from forms.newrouterform import new_route_planner
    from forms.dailyform import daily_reporting_form
    from forms.institutionform import institution_scorecard_report
    from forms.hcpformexistingworkplace import hcp_form_existing_workplace
    from forms.hcpformexistingaddress import hcp_form_existing_address
    from forms.hcpformnewclient import hcp_form_new_client

    # -----------LOAD DATA---------------------------------------------------------------
    from data import (
        load_route_data,
        load_daily_data,
        load_hcp_clients_data,
        load_institution_data,
        # load_pending_clients_data,
    )
    from dashboard import admin_dashboard
    import plotly.express as px
    import pytz
    from datetime import datetime
    from forms.newrouterform import get_week_of_month

    @st.fragment()
    def greetings():
        with st.container(key="my_header_container"):
            sac.alert(
                label="**Welcome**",
                description=f"""  <span style='color: {primary_color};'><strong>{user_credentials['fullname']}</strong></span>&nbsp;&nbsp;&nbsp;
                        (Territory: <span style='color:#000;'><strong>{user_credentials['Territory_ID']}</strong></span>)
                """,
                color="pink",
                icon="emoji-smile",
            )

    greetings()
    # now = pd.Timestamp.now()
    # current_week = now.isocalendar().week
    # st.write(current_week)
    # data = load_daily_data()
    # data["TimeStamp"] = data["TimeStamp"].str.replace("/", "-", regex=False)
    # data["TimeStamp"] = pd.to_datetime(
    #     data["TimeStamp"], errors="coerce", format="%d-%m-%Y %H:%M:%S"
    # )
    # time = data["TimeStamp"]
    # st.write(time)
    # dfweek = data["TimeStamp"].dt.isocalendar().week
    # st.write(dfweek)

    route_filters = [
        "Today",
        "Current Week",
        "Last Week",
        "Current Month",
        "Next Month",
        "Last Month",
        "Last 2 Months",
        "Last 6 Months",
        "Current Year",
    ]

    # Function to apply filters dynamically
    def apply_filters(data, selected_filter):
        # Ensure the TimeStamp column is in datetime format
        if "TimeStamp" in data.columns:
            data["TimeStamp"] = pd.to_datetime(
                data["TimeStamp"], errors="coerce", format="%d-%m-%Y %H:%M:%S"
            )
            now = pd.Timestamp.now()
            current_week = now.isocalendar().week
            current_year = now.year
            if selected_filter == "Today":
                today = pd.Timestamp.now().normalize()  # Normalize to remove time
                filtered_data = data[data["TimeStamp"].dt.date == today.date()]
            elif selected_filter == "Current Week":
                filtered_data = data[
                    data["TimeStamp"].dt.isocalendar().week == now.isocalendar().week
                ]
            elif selected_filter == "Current Month":
                filtered_data = data[data["TimeStamp"].dt.month == now.month]
            elif selected_filter == "Last Week":
                last_week = (current_week - 1) % 53 or 53  # Handle wraparound for weeks
                filtered_data = data[
                    (data["TimeStamp"].dt.isocalendar().week == last_week)
                    & (data["TimeStamp"].dt.year == current_year)
                ]
            elif selected_filter == "Next Month":
                next_month = (now.month % 12) + 1
                filtered_data = data[data["TimeStamp"].dt.month == next_month]
            elif selected_filter == "Last Month":
                last_month = now.month - 1 or 12
                filtered_data = data[data["TimeStamp"].dt.month == last_month]
            elif selected_filter == "Last 2 Months":
                last_two_months = [(now.month - i - 1) % 12 + 1 for i in range(2)]
                filtered_data = data[data["TimeStamp"].dt.month.isin(last_two_months)]
            elif selected_filter == "Last 6 Months":
                last_six_months = [(now.month - i - 1) % 12 + 1 for i in range(6)]
                filtered_data = data[data["TimeStamp"].dt.month.isin(last_six_months)]
            elif selected_filter == "Current Year":
                filtered_data = data[data["TimeStamp"].dt.year == now.year]

            else:
                filtered_data = data  # No filtering if selection is invalid
        else:
            st.error("The 'TimeStamp' column is missing or invalid.")
            filtered_data = data  # Default to no filtering
        return filtered_data

    # =============================TABS============================================
    with st.container(key="my_body_container"):
        tab = st.tabs(
            ["Route Planner", "Daily Reporting", "HCP / Retailers", "Dashboard"]
        )
        # --------------------ROUTE PLANNER TAB-------------------------------------
        with tab[0]:

            @st.fragment()
            def route_planner():
                # Define button container
                with st.container(key="route_buttons_container"):
                    # Expander for Action
                    with st.expander(
                        "Action", expanded=True, icon=":material/ads_click:"
                    ):
                        col1, col2, col3, col4 = st.columns(
                            [1, 2.5, 0.5, 1], vertical_alignment="bottom"
                        )
                        # Add Route Planner Button
                        with col1:

                            @st.dialog("Route Planner Form")
                            def show_route_form():
                                new_route_planner()

                            if st.button(
                                "Add Route",
                                help="Click to add route plan",
                                type="primary",
                                icon=":material/map:",
                                key="add_route_plan_button",
                                use_container_width=True,
                            ):
                                show_route_form()
                        # Refresh Button
                        with col3:
                            if st.button(
                                "",
                                help="Reload the data and clear cache.",
                                type="secondary",
                                icon=":material/refresh:",
                                key="refresh_route_planner",
                                use_container_width=True,
                            ):
                                st.cache_data.clear()  # Clear cached data
                                Route_data = load_route_data()  # Reload data
                                st.toast("Data refreshed successfully.", icon="✅")
                        with col4:
                            route_filters_section = st.empty()

                # Create empty container for dynamic table
                route_table_container = st.empty()
                Route_data = load_route_data()
                Route_data["TimeStamp"] = Route_data["TimeStamp"].str.replace(
                    "/", "-", regex=False
                )
                display_data = None
                # Add "Select All" at the beginning
                route_filters.insert(0, "Select All")
                filter_selection = route_filters_section.selectbox(
                    "Filter by",
                    options=route_filters,
                    index=1,
                    key="route_filter_select",
                )
                if "Select All" in filter_selection:
                    filter_selection = route_filters[1:]  # Exclude "Select All" itself

                # Check if data exists and process it
                if Route_data is not None and not Route_data.empty:
                    try:
                        # Filter by territory for non-admin users first
                        if user_territory != "admin":
                            if "Territory" in Route_data.columns:
                                Route_data = Route_data[
                                    Route_data["Territory"] == user_territory
                                ]
                            else:
                                st.error(
                                    "The 'Territory' column is missing in Route data."
                                )
                        # Now apply the selected filter
                        display_data = apply_filters(Route_data, filter_selection)
                        # Drop unnecessary columns based on user type
                        if user_territory != "admin":
                            display_data = display_data.drop(
                                columns=["TimeStamp", "Agent", "Territory"]
                            )
                        else:
                            display_data = display_data.drop(columns=["Month"])

                    except Exception as e:
                        st.error(f"Error processing data: {str(e)}")
                        st.exception(e)
                        display_data = None

                # Display data or show empty state
                with route_table_container:
                    if display_data is None or display_data.empty:
                        _, col, _ = st.columns([1, 3, 1], gap="small")
                        with col:
                            sac.result(
                                label="Oops! No data available for the selected filter. Please try a different filter.",
                                status="empty",
                                key="router_table_empty_state",
                            )
                    else:
                        st.dataframe(
                            display_data,
                            use_container_width=True,
                            height=600,
                            hide_index=True,
                        )

            route_planner()

        # --------------------DAILY REPORTING TAB----------------------------------------------------------------
        with tab[1]:
            data = {
                "Appointment / Follow-Up": "Scheduled future visits or calls with a contact to discuss the product or check on stock levels. OR required to for a follow-up.",
                "Closed": "The institution/store/shop wasn't open or permanently closed down.",
                "Codes inactive": "Products were inactive or out of stock, No further action or stocking.",
                "Commitment": "A commitment made by a contact (e.g., nurse, pharmacist) to order, recommend, or prescribe Alpha.",
                "Complaint": "Feedback provided that raises issues or concerns about the product, stock, or service.",
                "Confirm to Order": "Confirmation from the contact that they will place an order for the product.",
                "Contact HQ": "Action item to reach out to headquarters for additional support or information.",
                "Delivered": "The product was delivered to the facility and confirmed as received.",
                "Introduction-Product Discussion": "Conversation introducing the product or discussing its benefits or use cases.",
                "No Discussions": "No meaningful discussion or engagement took place during the visit./couldn't reach the contact person.",
                "Not Stocking": "The facility or pharmacy is not currently or in the near future planning to stock the product.",
                "Ordered": "The facility placed an order for the product.",
                "Other Supplier": "The contact is sourcing products from another supplier (e.g., Citylink, Veteran).",
                "Promise": "The verbal promise from the contact to place an order or recommend or prescribe the product in the future.",
                "Sample": "A request for or delivery of product samples to the contact or facility.",
                "Stocked": "The facility already has the product in stock.",
                "Unavailable": "The contact/decision-maker of the facility was not available during the visit.",
            }

            # with st.container(key="daily_buttons_container"):
            @st.fragment()
            def dailyReport():
                # Expander for Action
                with st.expander("Action", expanded=True, icon=":material/ads_click:"):
                    col1, col2, col3, col4, col5, dailyFilterCol = st.columns(
                        [1.5, 1.5, 2, 0.5, 0.5, 1.5], vertical_alignment="bottom"
                    )
                    with col1:

                        @st.dialog("Daily Activity Form")
                        def show_daily_form():
                            daily_reporting_form()

                        if st.button(
                            "Client Report",
                            help="Click to add activity",
                            type="primary",
                            icon=":material/group_add:",
                            key="add_daily_client_report_form_button",
                            use_container_width=True,
                        ):

                            show_daily_form()

                    with col2:

                        @st.dialog("Institution's Scorecard Report")
                        def show_institution_scorecard_report():
                            institution_scorecard_report()

                        if st.button(
                            "Institution Report",
                            help="Click to add activity",
                            type="primary",
                            icon=":material/add_home_work:",
                            key="add_daily_institution_Report_form_button",
                            use_container_width=True,
                        ):
                            show_institution_scorecard_report()
                    with col4:
                        # Refresh Button
                        if st.button(
                            "",
                            help="Click to Refresh Data",
                            type="secondary",
                            icon=":material/refresh:",
                            key="refresh_daily_form",
                            use_container_width=True,
                        ):
                            st.cache_data.clear()  # Clear the cache
                            st.toast("Cache cleared. Reloading data...", icon="✅")
                    with col5:

                        @st.dialog("Outcome Explanations")
                        def show_outcomes():
                            st.write(
                                "Explore the various outcomes and their explanations below:"
                            )
                            for outcome, explanation in data.items():
                                st.markdown(f"- **{outcome}**: {explanation}")

                        if st.button(
                            "",
                            icon=":material/info:",
                            key="outcomes_button",
                            help="Click to view outcomes",
                            use_container_width=True,
                        ):
                            show_outcomes()
                    with dailyFilterCol:
                        filter_section = st.empty()
                with st.expander(
                    "CLIENTS DAILY REPORTING", icon=":material/ballot:", expanded=True
                ):
                    # Create empty container for dynamic table
                    daily_table_container = st.empty()
                    Daily_data = load_daily_data()
                    display_daily_data = None
                    # Convert Timestamp column to datetime with mixed format and then to ISO format
                    Daily_data["TimeStamp"] = Daily_data["TimeStamp"].str.replace(
                        "/", "-", regex=False
                    )
                    Daily_data["TimeStamp"] = pd.to_datetime(
                        Daily_data["TimeStamp"],
                        errors="coerce",
                        dayfirst=True,
                        format="%d-%m-%Y %H:%M:%S",
                    )  # Convert to ISO format
                    # Select box for filters
                    filter_selection = filter_section.selectbox(
                        "Filter by",
                        options=route_filters,
                        index=1,
                        key="daily_filter_selection",
                    )
                    # Check if data exists and process it
                    if Daily_data is not None and not Daily_data.empty:
                        try:
                            # Filter by territory for non-admin users first
                            if user_territory != "admin":
                                if "Territory" in Daily_data.columns:
                                    Daily_data = Daily_data[
                                        Daily_data["Territory"] == user_territory
                                    ]
                                else:
                                    st.error(
                                        "The 'Territory' column is missing in Daily data."
                                    )
                            # Now apply the selected filter
                            display_daily_data = apply_filters(
                                Daily_data, filter_selection
                            )
                            # Drop unnecessary columns based on user type
                            if user_territory != "admin":
                                display_daily_data = display_daily_data.drop(
                                    columns=["TimeStamp", "Agent_Name", "Territory"]
                                )
                            else:
                                display_daily_data = display_daily_data.drop(
                                    columns=["Month"]
                                )
                        except Exception as e:
                            st.error(f"Error processing data: {str(e)}")
                            st.exception(e)
                            display_daily_data = None
                    # Display data or show empty state
                    with daily_table_container:
                        if display_daily_data is None or display_daily_data.empty:
                            _, col, _ = st.columns([1, 3, 1], gap="small")
                            with col:
                                sac.result(
                                    label="Oops! No data available for the selected filter. Please try a different filter.",
                                    status="empty",
                                    key="daily_table_empty_state",
                                )
                        else:
                            st.dataframe(
                                display_daily_data, height=600, hide_index=True
                            )

                    # -----------------INSTITUTION DATA---------------------------------------------------
                with st.expander(
                    "INSTITUTION SCORECARD",
                    icon=":material/add_home_work:",
                    expanded=True,
                ):
                    filter_institu_selection = st.empty()
                    # Create empty container for dynamic table
                    institution_scorecard_table_container = st.empty()
                    Institution_data = load_institution_data()
                    Institution_data["TimeStamp"] = Institution_data[
                        "TimeStamp"
                    ].str.replace("/", "-", regex=False)
                    display_Institution_data = None
                    # Select box for filters
                    filter_selection = filter_institu_selection.selectbox(
                        "Filter by",
                        options=route_filters,
                        index=1,
                        key="filter_institution_selection",
                    )
                    # Check if data exists and process it
                    if Institution_data is not None and not Institution_data.empty:
                        try:
                            # Filter by territory for non-admin users first
                            if user_territory != "admin":
                                if "Territory" in Institution_data.columns:
                                    Institution_data = Institution_data[
                                        Institution_data["Territory"] == user_territory
                                    ]
                                else:
                                    st.error(
                                        "The 'Territory' column is missing in Daily data."
                                    )
                            # Now apply the selected filter
                            display_Institution_data = apply_filters(
                                Institution_data, filter_selection
                            )
                            # Drop unnecessary columns based on user type
                            if user_territory != "admin":
                                display_Institution_data = (
                                    display_Institution_data.drop(
                                        columns=["TimeStamp", "Agent_Name", "Territory"]
                                    )
                                )
                            else:
                                display_Institution_data = (
                                    display_Institution_data.drop(columns=["Month"])
                                )
                        except Exception as e:
                            st.error(f"Error processing data: {str(e)}")
                            st.exception(e)
                            display_Institution_data = None
                    # Display data or show empty state
                    with institution_scorecard_table_container:
                        if (
                            display_Institution_data is None
                            or display_Institution_data.empty
                        ):
                            _, col, _ = st.columns([1, 3, 1], gap="small")
                            with col:
                                sac.result(
                                    label="Oops! No data available for the selected filter. Please try a different filter.",
                                    status="empty",
                                    key="institution_table_empty_state",
                                )
                        else:
                            st.dataframe(
                                display_Institution_data, height=600, hide_index=True
                            )

            dailyReport()

        # --------------------HCP / RETAILERS TAB----------------------------------------------------------------
        with tab[2]:

            @st.fragment()
            def hcp_reporting():
                # Expander for Action
                with st.expander("Action", expanded=True, icon=":material/ads_click:"):
                    with st.container():
                        col1, col2, col3, col4 = st.columns([1, 1, 1, 0.4], gap="small")
                        with col1:

                            @st.dialog("New HCP/Client/Retailer Form")
                            def show_hcp_form_new_client():
                                hcp_form_new_client()

                            if st.button(
                                # "Add Client (New Workplace & New Address)",
                                "Add Client(Completely New)",
                                help="Click to add new HCP/Client/Retailer",
                                type="primary",
                                icon=":material/person_add:",
                                key="add_hcp_form_button",
                                use_container_width=True,
                            ):
                                show_hcp_form_new_client()

                        with col2:

                            @st.dialog("Add Client to Existing Workplace")
                            def show_hcp_form_existing_workplace():
                                hcp_form_existing_workplace()

                            if st.button(
                                "Add Client (Existing Workplace)",
                                help="Click to new client to an existing workplace",
                                type="primary",
                                icon=":material/add_business:",
                                key="add_hcp_form_existing_button",
                                use_container_width=True,
                            ):
                                show_hcp_form_existing_workplace()
                        with col3:

                            @st.dialog("Add Client to Existing Address")
                            def show_hcp_form_existing_address():
                                hcp_form_existing_address()

                            if st.button(
                                "Add Client (Existing Address)",
                                help="Click to add new Workplace to an existing address",
                                type="primary",
                                icon=":material/add_location:",
                                key="add_hcp_form_existing_address_button",
                                use_container_width=True,
                            ):
                                show_hcp_form_existing_address()
                        with col4:
                            if st.button(
                                "",
                                help="Click to Refresh Data",
                                type="secondary",
                                icon=":material/refresh:",
                                key="refresh_hcp_form",
                                use_container_width=True,
                            ):
                                st.cache_data.clear()
                                st.toast("Cache cleared. Reloading data...", icon="✅")

                    # ----------PENDING DATA ------------------------------------------------------------
                    # pending_clients_data = load_pending_clients_data()
                    # display_pending_data = None
                    # # Check if data exists and process it
                    # if pending_clients_data is not None and not pending_clients_data.empty:
                    #     try:
                    #         # Filter by territory for non-admin users
                    #         if user_territory != "admin":
                    #             pending_clients_data = pending_clients_data[
                    #                 pending_clients_data["Territory"] == user_territory
                    #             ]
                    #             if not pending_clients_data.empty:
                    #                 display_pending_data = pending_clients_data.drop(
                    #                     columns=["Territory", "Workplace_Type", "State"]
                    #                 )  # Drop Territory column for non-admin users
                    #         else:
                    #             display_pending_data = pending_clients_data.copy()
                    #     except Exception as e:
                    #         st.error(f"Error processing data: {str(e)}")
                    #         display_pending_data = None
                    # # Display data or show empty state
                    # if display_pending_data is None or display_pending_data.empty:
                    #     col1, col2, col3 = st.columns(3, gap="small")
                    #     with col2:
                    #         sac.result(
                    #             label="Oops! No data available. Please add to view.",
                    #             status="empty",
                    #             key="pending_table_empty_state",
                    #         )
                    # else:
                    #     st.dataframe(display_pending_data, hide_index=True)

                # Create empty container for dynamic table
                hcp_table_container = st.empty()
                HCP_Clients_data = load_hcp_clients_data()
                # Check if data exists and process it
                if HCP_Clients_data is not None and not HCP_Clients_data.empty:
                    try:
                        # Filter by territory for non-admin users
                        if user_territory != "admin":
                            HCP_Clients_data = HCP_Clients_data[
                                HCP_Clients_data["Territory"] == user_territory
                            ]
                            if not HCP_Clients_data.empty:
                                display_hcp_data = HCP_Clients_data.drop(
                                    columns=[
                                        "Territory",
                                        "Workplace_Type",
                                        "State",
                                        "TimeStamp",
                                    ]
                                )  # Drop Territory column for non-admin users
                        else:
                            display_hcp_data = HCP_Clients_data.copy()
                    except Exception as e:
                        st.error(f"Error processing data: {str(e)}")
                        display_hcp_data = None
                # Display data or show empty state
                with hcp_table_container:
                    if display_hcp_data is None or display_hcp_data.empty:
                        _, col, _ = st.columns([1, 3, 1], gap="small")
                        with col:
                            sac.result(
                                label="Oops! No data available. Please add to view.",
                                status="empty",
                                key="hcp_table_empty_state",
                            )
                    else:
                        st.dataframe(display_hcp_data, height=600, hide_index=True)

            hcp_reporting()

        # ---- DASHBOARD TAB ---------------------------------------------------------------
        with tab[3]:
            dashboard_container = st.empty()

            @st.fragment()
            def user_dashboard():
                with st.expander(
                    "Metrics Summary - (based on clients reports)",
                    icon=":material/bar_chart:",
                    expanded=False,
                ):
                    # st.write(user_territory)
                    territory = user_territory
                    clientdata = load_daily_data()
                    clientdata["TimeStamp"] = clientdata["TimeStamp"].str.replace(
                        "/", "-"
                    )
                    clientdata["TimeStamp"] = pd.to_datetime(
                        clientdata["TimeStamp"],
                        format="%d-%m-%Y %H:%M:%S",
                        dayfirst=True,
                        errors="coerce",
                    )
                    # Filter the DataFrame based on the user's territory
                    user_data_df = clientdata[
                        clientdata["Territory"].str.strip() == territory
                    ]

                    if user_data_df.empty:
                        st.warning(f"No data available for territory: {territory}")

                    # Calculate metrics for the filtered data
                    current_time = datetime.now()
                    total_reports = len(user_data_df)
                    reports_this_year = len(
                        user_data_df[
                            user_data_df["TimeStamp"].dt.year == current_time.year
                        ]
                    )
                    reports_this_month = len(
                        user_data_df[
                            user_data_df["TimeStamp"].dt.month == current_time.month
                        ]
                    )
                    total_reports = f"{total_reports} ({reports_this_year} this year) ({reports_this_month} this month)"

                    last_updated = user_data_df["TimeStamp"].max()

                    # Time since the last update
                    if pd.isna(last_updated) or last_updated is pd.NaT:
                        last_updated_str = "N/A"
                        time_since_last_update = "N/A"
                    else:
                        last_updated_str = last_updated.strftime("%d-%m-%Y")
                        time_ago = (current_time - last_updated).total_seconds()
                        days_ago = time_ago // (24 * 3600)
                        hours_ago = (time_ago % (24 * 3600)) // 3600
                        minutes_ago = (time_ago % 3600) // 60
                        seconds_ago = time_ago % 60
                        time_since_last_update = f"{int(days_ago)} Days {int(hours_ago)} hrs {int(minutes_ago)} mins {int(seconds_ago)} secs"

                    # Display metrics in columns
                    cols = st.columns(3)
                    with cols[0]:
                        ui.metric_card(
                            title="Last Updated",
                            content=f"""{last_updated_str}""",
                            description=None,
                            key="user_metric_card1",
                        )
                    with cols[1]:
                        ui.metric_card(
                            title="Time of the last update",
                            content=f"""{time_since_last_update}""",
                            description=None,
                            key="user_metric_card2",
                        )
                    with cols[2]:
                        ui.metric_card(
                            title="Total Reports",
                            content=f"{total_reports}",
                            description=None,
                            key="user_metric_card3",
                        )

                # ====================DEAL SIZE/LPO TRENDS===================================================================
                with st.expander(
                    "Deal Size/LPO Trends",
                    icon=":material/shopping_cart:",
                    expanded=False,
                ):

                    def current_time():
                        timezone = pytz.timezone("Africa/Nairobi")
                        return datetime.now(timezone)

                    def get_current_month_details():
                        current_date = current_time()
                        current_month = current_date.strftime("%b")
                        return current_month

                    def get_month_options():
                        return [
                            datetime(2024, m, 1).strftime("%b") for m in range(1, 13)
                        ]

                    clients_dailyrpt_df = load_institution_data()
                    clients_dailyrpt_df = clients_dailyrpt_df[
                        clientdata["Territory"].str.strip() == territory
                    ]
                    clients_dailyrpt_df["TimeStamp"] = clients_dailyrpt_df[
                        "TimeStamp"
                    ].str.replace("/", "-")
                    clients_dailyrpt_df["TimeStamp"] = pd.to_datetime(
                        clients_dailyrpt_df["TimeStamp"],
                        dayfirst=True,
                        errors="coerce",
                        format="%d-%m-%Y %H:%M:%S",
                    )

                    # Extract date (optional, depending on your level of granularity)
                    clients_dailyrpt_df["Date"] = clients_dailyrpt_df[
                        "TimeStamp"
                    ].dt.date
                    clients_dailyrpt_df["Year"] = clients_dailyrpt_df[
                        "TimeStamp"
                    ].dt.year
                    clients_dailyrpt_df["Day"] = clients_dailyrpt_df[
                        "TimeStamp"
                    ].dt.date
                    territories = clients_dailyrpt_df["Workplace"].unique().tolist()

                    (
                        territory_filters,
                        yr_filters,
                        mnth_filters,
                        wk_filters,
                        day_filters,
                    ) = st.columns([1, 1, 1, 1, 1])
                    # ---------------FILTERS
                    # Add "Select All" at the beginning
                    territories.insert(0, "Select All")
                    with territory_filters:
                        territory_filter = st.selectbox(
                            "Workplace",
                            options=territories,
                            index=0,
                            key="lpo_territory_filter",
                        )
                    with yr_filters:
                        year_options = sorted(clients_dailyrpt_df["Year"].unique())
                        year_options.insert(
                            0, "Select All"
                        )  # Add "Select All" at the beginning
                        yr_filter = st.selectbox(
                            "Year",
                            options=year_options,
                            index=0,
                            key="lpoyr_filter",
                        )
                    with mnth_filters:
                        month_options = get_month_options()
                        month_options.insert(
                            0, "Select All"
                        )  # Add "Select All" at the beginning
                        mnth_filter = st.selectbox(
                            "Month",
                            options=month_options,
                            index=0,
                            key="lpomnth_filter",
                        )
                    with wk_filters:
                        week_options = get_week_of_month()
                        week_options.insert(
                            0, "Select All"
                        )  # Add "Select All" at the beginning
                        wk_filter = st.selectbox(
                            "Week",
                            options=week_options,
                            index=0,
                            key="lpowk_filter",
                        )
                    with day_filters:
                        day_filter = st.date_input(
                            "Date",
                            value=None,
                            # format="DD-MM-YYYY",
                            key="lpodate_filter",
                        )

                    # Create a time series plot
                    def plot_time_series(data, show_legend):
                        fig = px.line(
                            data,
                            x="Date",
                            y="Value",
                            color="LPO_Type",
                            labels={
                                "Date": "Date",
                                "Value": "LPO Value",
                                "LPO_Type": "LPO Category",
                            },
                            color_discrete_sequence=px.colors.sequential.Rainbow,
                            line_shape="spline",
                        )
                        fig.update_traces(
                            mode="lines+markers"
                        )  # Add markers for better visibility
                        fig.update_layout(
                            xaxis=dict(showgrid=False),
                            yaxis=dict(showgrid=False),
                            height=600,
                            showlegend=show_legend,
                        )
                        return fig

                    # Function to generate Bar Chart
                    def plot_bar_chart(data, show_legend):
                        fig = px.bar(
                            data,
                            x="Date",
                            y="Value",
                            color="LPO_Type",
                            labels={
                                "Date": "Date",
                                "Value": "LPO Value",
                                "LPO_Type": "LPO Category",
                            },
                            color_discrete_sequence=px.colors.sequential.Rainbow,
                            barmode="group",
                        )
                        fig.update_layout(
                            xaxis=dict(showgrid=False),
                            yaxis=dict(showgrid=False, showticklabels=False),
                            height=600,
                            showlegend=show_legend,
                        )
                        # Add data labels to the bars
                        fig.update_traces(
                            textposition="outside",
                            textfont=dict(size=12),
                            text=data["Value"],
                        )
                        return fig

                    # Filter data based on selected filters
                    filtered_data = clients_dailyrpt_df
                    if territory_filter != "Select All":
                        filtered_data = filtered_data[
                            filtered_data["Territory"] == territory_filter
                        ]
                    else:
                        territory_filter = territories[1:]

                    if yr_filter != "Select All":
                        filtered_data = filtered_data[
                            filtered_data["Year"] == yr_filter
                        ]
                    else:
                        yr_filter = yr_filter[1:]

                    if mnth_filter != "Select All":
                        filtered_data = filtered_data[
                            filtered_data["Month"] == mnth_filter
                        ]
                    else:
                        mnth_filter = mnth_filter[1:]

                    if wk_filter != "Select All":
                        filtered_data = filtered_data[
                            filtered_data["Week"] == wk_filter
                        ]
                    else:
                        wk_filter = wk_filter[1:]
                    if day_filter:
                        filtered_data = filtered_data[
                            filtered_data["Day"] == day_filter
                        ]

                    # Group filtered data for visualization
                    filtered_data = (
                        filtered_data.groupby(
                            [
                                "Date",
                                "Territory",
                                "LPO(A1)",
                                "LPO(A2)",
                                "TotalLPO",
                            ]
                        )
                        .size()
                        .reset_index(name="Count")
                    )
                    grouped_filtered_data = filtered_data.melt(
                        id_vars=["Date"],
                        value_vars=[
                            "LPO(A1)",
                            "LPO(A2)",
                            "TotalLPO",
                        ],  # Specify the columns to plot
                        var_name="LPO_Type",
                        value_name="Value",
                    )

                    brchrttggl, lgndtgl = st.columns(2)
                    with brchrttggl:
                        # Create the toggle switch using shadcn library
                        chart_toggle = ui.switch(
                            default_checked=False,
                            label="Switch to Bar Chart",
                            key="lposwitch_visualization",
                        )
                    with lgndtgl:
                        # Create the toggle switch for showing/hiding the legend
                        legend_toggle = ui.switch(
                            default_checked=False,
                            label="Legend",
                            key="lpolegend_toggle",
                        )
                    # Get the value of the legend toggle
                    show_legend = legend_toggle
                    # Create and display the Plotly chart
                    if not grouped_filtered_data.empty:
                        if chart_toggle:
                            st.plotly_chart(
                                plot_bar_chart(grouped_filtered_data, show_legend),
                                use_container_width=True,
                            )
                        else:
                            st.plotly_chart(
                                plot_time_series(grouped_filtered_data, show_legend),
                                use_container_width=True,
                            )
                    else:
                        sac.result(
                            label="Oops! No data available for the selected filter. Please try a different filter.",
                            status="empty",
                            key="lporouter_table_empty_state",
                        )
                # ======================CLIENTS DISTRIBUTION===================================================================
                with st.expander(
                    "Clients Distribution",
                    icon=":material/groups:",
                    expanded=True,
                ):
                    clients_db = load_hcp_clients_data()
                    # useragenttotalclients = len(clients_db)
                    clients_db = clients_db[
                        clients_db["Territory"].str.strip() == user_territory
                    ]
                    useragenttotalclients = len(clients_db)
                    st.metric(
                        label="Total Clients",
                        value=useragenttotalclients,
                    )
                    (
                        address_filters,
                        workplaceType_filters,
                        workplace_filters,
                        _,
                        clearfilters,
                    ) = st.columns([1, 1, 1, 1, 1], vertical_alignment="bottom")
                    with clearfilters:

                        def reset_filters():
                            st.session_state.clntdb_territory_filter = "Select All"
                            st.session_state.clntdb_workplaceType_filter = "Select All"
                            st.session_state.clntdb_workplace_filter = "Select All"

                        # Add a reset button
                        if st.button(
                            "Reset Filters",
                            icon=":material/rule_settings:",
                            key="reset_userclntdb_filters",
                        ):
                            reset_filters()
                    # ---------------FILTERS
                    addresses = clients_db["Line_Address"].unique().tolist()
                    addresses.insert(
                        0, "Select All"
                    )  # Add "Select All" at the beginning
                    with address_filters:
                        address_filter = st.selectbox(
                            "Address",
                            options=addresses,
                            index=0,
                            key="clntdb_territory_filter",
                        )
                    with workplaceType_filters:
                        workplaceTypes = sorted(clients_db["Workplace_Type"].unique())
                        workplaceTypes.insert(0, "Select All")
                        workplaceType_filter = st.selectbox(
                            "Workplace Type",
                            options=workplaceTypes,
                            index=0,
                            key="clntdb_workplaceType_filter",
                        )
                    with workplace_filters:
                        workplace_filters = sorted(clients_db["Workplace"].unique())
                        workplace_filters.insert(0, "Select All")
                        workplace_filter = st.selectbox(
                            "Workplace",
                            options=workplace_filters,
                            index=0,
                            key="clntdb_workplace_filter",
                        )

                    # Filter data based on selected filters
                    filtered_data = clients_db
                    if address_filter != "Select All":
                        filtered_data = filtered_data[
                            filtered_data["Line_Address"] == address_filter
                        ]
                    else:
                        address_filter = addresses[1:]

                    if workplaceType_filter != "Select All":
                        filtered_data = filtered_data[
                            filtered_data["Workplace_Type"] == workplaceType_filter
                        ]
                    else:
                        workplaceType_filter = workplaceTypes[1:]
                    if workplace_filter != "Select All":
                        filtered_data = filtered_data[
                            filtered_data["Workplace"] == workplace_filter
                        ]
                    else:
                        workplace_filter = workplace_filters[1:]

                    # Function to generate Bar Chart
                    def plot_bar_chart(data, show_legend):
                        data = data.sort_values(by="Count", ascending=False)
                        fig = px.bar(
                            data,
                            x="Cadre",
                            y="Count",
                            color="Cadre",
                            labels={"Count": "Number of Clients"},
                            color_discrete_sequence=px.colors.sequential.Rainbow,
                            text="Count",
                        )
                        fig.update_layout(
                            xaxis=dict(showgrid=False),
                            yaxis=dict(showgrid=False, showticklabels=False),
                            height=600,
                            showlegend=show_legend,
                        )
                        # Add data labels to the bars
                        fig.update_traces(
                            textposition="outside",
                            textfont=dict(size=12),
                        )

                        return fig

                    # Group filtered data for visualization
                    grouped_filtered_data = (
                        filtered_data.groupby("Cadre").size().reset_index(name="Count")
                    )

                    # Create the toggle switch for showing/hiding the legend
                    legend_toggle = ui.switch(
                        default_checked=False,
                        label="Legend",
                        key="clntdblegend_toggle",
                    )
                    # Get the value of the legend toggle
                    show_legend = legend_toggle
                    # Create and display the Plotly chart
                    if not grouped_filtered_data.empty:
                        st.plotly_chart(
                            plot_bar_chart(grouped_filtered_data, show_legend),
                            use_container_width=True,
                        )
                    else:
                        sac.result(
                            label="Oops! No data available for the selected filter. Please try a different filter.",
                            status="empty",
                            key="lporouter_table_empty_state",
                        )

            # ----------------------------------------------------------------------------------------------------------------------------------------------------------
            if user_role == "Admin":
                with dashboard_container.container():
                    admin_dashboard()
            if user_role == "User":
                user_dashboard()

        # --------------------------------------------------------s------------------------------------------------------------------

        with st.container(key="divider_logout"):
            st.divider()
        # ---- LOGOUT BUTTON ---------------------------------------------------------------
        _, lgt = st.columns([3, 1])
        with lgt:
            with st.expander("Logout", icon=":material/logout:"):
                if Authenticator.logout("Logout", "main"):
                    with st.spinner("Logging out..."):
                        # Clear all authentication-related session state
                        for key in [
                            "authenticated",
                            "username",
                            "name",
                            "credentials",
                            "user_credentials",
                            "authentication_status",
                        ]:
                            if key in st.session_state:
                                del st.session_state[key]
                        st.write("You have logged out successfully.")

        now = pd.Timestamp.now()
        current_year = now.year
        # Add the copyright line dynamically
        st.markdown(
            f"""
             <div style="margin-left: 20px;">
            &copy; {current_year} Alpha Plus Group. &nbsp;&nbsp;&nbsp; All rights reserved.
            </div>
            """,
            unsafe_allow_html=True,
        )
elif st.session_state["authentication_status"] is False:
    with col2:
        st.error("Username/password is incorrect")
elif st.session_state["authentication_status"] is None:
    with col2:
        st.info("Please enter your username and password")
