import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import time
import pytz

# # --------------------AUTHENTICATION CHECK---------------------------------------------------------------
# if not st.session_state.get("authenticated"):
#     st.error("Please login to access this page")
#     st.stop()

# # --------------------GET USER SPECIFIC DATA(Signed in user)---------------------------------------------------------------
# username = st.session_state["username"]
# user_credentials = st.session_state["user_credentials"]
# # user_credentials = st.session_state["credentials"]["usernames"][username]
# user_territory = user_credentials["Territory_ID"]
# user_role = user_credentials["role"]
# user_fullname = user_credentials["fullname"]


# --------------------LOAD CUSTOM CSS---------------------------------------------------------------
def load_custom_css():
    with open("assets/css/style.css", "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


load_custom_css()


# --------------------CURRENT TIME---------------------------------------------------------------
def current_time():
    timezone = pytz.timezone("Africa/Nairobi")  # Setting timezone to East Africa
    return datetime.now(timezone)


# --------------------LOAD CLIENTS DATABASE---------------------------------------------------------------


# Cache the function to avoid reloading data on each action--------------
@st.cache_data(ttl=300)
def fetch_data():
    # Establishing Google Sheets connection--------------------------------
    conn = st.connection("gsheets", type=GSheetsConnection)
    clients_list_data = conn.read(worksheet="ClientsDatabase")
    existing_pending_clients_data = conn.read(worksheet="PendingClients")
    users = conn.read(worksheet="Users")
    cadre = conn.read(worksheet="Cadre")
    institution_types = conn.read(worksheet="Type")
    institutions_department = conn.read(worksheet="Department")
    cycle_goals = conn.read(worksheet="Cycle_Goals")
    product_px_reco = conn.read(worksheet="Products")
    return (
        clients_list_data,
        existing_pending_clients_data,
        users,
        cadre,
        institution_types,
        institutions_department,
        cycle_goals,
        product_px_reco,
    )


# Add new function to get agent names
def get_agent_names(users_df):
    # Filter users by role="User" and get their names and territory IDs
    agents = users_df[users_df["role"] == "User"][["name", "Territory_ID"]]
    return dict(zip(agents["name"], agents["Territory_ID"]))


# --------------------BUILD HIERARCHICAL DATA---------------------------------------------------------------
@st.cache_data(persist=True)
# @st.cache_data(ttl=300)
def build_hierarchical_data(df, territory_id=None):
    # Filter data by territory if provided
    if territory_id:
        df = df[df["Territory"] == territory_id]

    cached_data = {}
    client_id_data = {}
    workplace_details = {}  # New dictionary to store workplace details

    for _, row in df.iterrows():
        client_id = str(row["Client_ID"])
        address = str(row["Line_Address"])
        work_place = str(row["Workplace"])
        client_name = str(row["Client_Name"])

        # Store workplace details
        workplace_key = f"{address}_{work_place}"
        workplace_details[workplace_key] = {
            "Workplace_Type": row.get("Workplace_Type", ""),
            "City": row.get("City", ""),
            "Postal_Area": row.get("Postal_Area", ""),
            "State": row.get("State", ""),
        }

        # Build client_id hierarchy
        if address not in client_id_data:
            client_id_data[address] = client_id

        # Build work_place and client_name hierarchy
        if address not in cached_data:
            cached_data[address] = {}

        if work_place not in cached_data[address]:
            cached_data[address][work_place] = []

        if client_name not in cached_data[address][work_place]:
            cached_data[address][work_place].append(client_name)

    # Sort the data
    cached_data = {
        k: {wk: sorted(wv) for wk, wv in v.items()}
        for k, v in sorted(cached_data.items())
    }

    return cached_data, client_id_data, workplace_details


# --------------------DAILY REPORTING FORM---------------------------------------------------------------
def clear_form():
    """Clears the form input fields."""
    st.session_state["hcp_clientaddressselectedaddress"] = None
    st.session_state["hcp_clientselectedworkplace"] = None
    st.session_state["hcp_department"] = None
    st.session_state["hcp_prefix"] = None
    st.session_state["hcp_inputclient"] = ""
    st.session_state["hcp_cadre"] = None
    st.session_state["hcp_colour_codes"] = None
    st.session_state["hcp_adoption_ladder"] = 0
    st.session_state["hcp_six_months_section"] = 0
    st.session_state["hcp_one_year_section"] = 0
    st.session_state["hcp_three_years_section"] = 0
    st.session_state["hcp_potentiality"] = None
    st.session_state["hcp_level_of_influence"] = None
    st.session_state["hcp_cycle_goals"] = None
    st.session_state["hcp_product_px_reco"] = []


def hcp_form_existing():
    if "show_clear_button" not in st.session_state:
        st.session_state.show_clear_button = False
    f3, f4 = st.columns(2, gap="medium")
    with f4:
        if st.button(
            label="Clear",
            on_click=clear_form,
            use_container_width=True,
            icon=":material/clear_all:",
            key="clear_daily_form",
        ):
            clear_form()

    (
        clients_list_data,
        existing_pending_clients_data,
        users,
        cadre,
        institution_types,
        institutions_department,
        cycle_goals,
        product_px_reco,
    ) = fetch_data()

    # List of data imports from sheets
    PREFIXES = ["Mr.", "Mrs.", "Ms.", "Dr.", "Prof."]
    COLORCODES = ["RED", "BLUE", "GREEN", "YELLOW"]
    CADRE = cadre["Cadre"].unique().tolist()
    TYPE = institution_types["Type"].unique().tolist()
    DEPARTMENT = institutions_department["Department"].unique().tolist()
    GOALS = cycle_goals["Cycle_Goals"].unique().tolist()
    PRODUCTS = product_px_reco["Products"].unique().tolist()

    # Sorted lists
    PREFIXES = sorted(PREFIXES)
    COLORCODES = sorted(COLORCODES)
    CADRE = sorted(CADRE)
    TYPE = sorted(TYPE)
    DEPARTMENT = sorted(DEPARTMENT)
    GOALS = sorted(GOALS)
    PRODUCTS = sorted(PRODUCTS)

    # Labels with HTML formatting for font size control
    adoption_ladder_label = """
        <p>Adoption Ladder</p>
        <ul style="font-size: 0.2em; color: gray;">
            <li><b>0-2</b>: RED</li>
            <li><b>3-6</b>: BLUE</li>
            <li><b>7-8</b>: GREEN</li>
            <li><b>9-10</b>: YELLOW</li>
        </ul>
    """

    potentiality_label = """
        <p>Potentiality</p>
        <ul style="font-size: 0.2em; color: gray;">
            <li>More than 150 babies per month - <b>(High)</b></li>
            <li>More than 100 but not greater than 150 babies per month - <b>(Moderate)</b></li>
            <li>Less than 100 babies per month - <b>(Low)</b></li>
        </ul>
    """

    section_label = """
    ### Section: Reach
    For the next 3 Questions, input estimates as numbers.
    """

    # Get agent names and their territories
    agent_territories = get_agent_names(users)

    # Add agent selection at the top
    selected_agent = st.selectbox(
        label="Select Your Name*",
        options=sorted(agent_territories.keys()),
        index=None,
        key="hcp_selected_agent",
    )

    # Get territory ID for selected agent
    selected_territory = (
        agent_territories.get(selected_agent) if selected_agent else None
    )

    # Build hierarchical data filtered by territory
    cached_data, client_id_data, workplace_details = (
        build_hierarchical_data(clients_list_data, territory_id=selected_territory)
        if selected_territory
        else ({}, {}, {})
    )

    selected_address = st.selectbox(
        label="Select Client Address",
        options=cached_data.keys() if cached_data else [],
        placeholder="select address",
        key="hcp_clientaddressselectedaddress",
    )

    selected_workplace = st.selectbox(
        label="Select Client Workplace",
        options=(
            sorted(cached_data[selected_address].keys())
            if selected_address and selected_address in cached_data
            else []
        ),
        placeholder="select a work_place",
        key="hcp_clientselectedworkplace",
    )

    department = st.selectbox(
        label="Department",
        options=DEPARTMENT,
        key="hcp_department",
        index=None,
    )

    prefix = st.selectbox(
        label="Prefix",
        options=PREFIXES,
        key="hcp_prefix",
        index=None,
    )

    client_name = st.text_input(
        label="Client Name. eg; John Doe",
        key="hcp_inputclient",
    )

    cadre = st.selectbox(
        label="Cadre",
        options=CADRE,
        key="hcp_cadre",
        index=None,
    )

    colour_codes = st.selectbox(
        "Colour CODE*", options=COLORCODES, index=None, key="hcp_colour_codes"
    )

    st.markdown(
        adoption_ladder_label,
        unsafe_allow_html=True,
    )

    adoption_ladder = st.number_input(
        label="Pick a number between 0 and 10*",
        min_value=0,
        max_value=10,
        value=None,
        step=1,
        key="hcp_adoption_ladder",
    )

    st.markdown(section_label)
    six_months_section = st.number_input(
        label="Number of babies seen in 0 - 6 Months*",
        min_value=0,
        value=None,
        step=1,
        key="hcp_six_months_section",
    )

    one_year_section = st.number_input(
        label="Number of babies seen in 6 months - 1 Year*",
        min_value=0,
        value=None,
        step=1,
        key="hcp_one_year_section",
    )

    three_years_section = st.number_input(
        label="Number of babies seen in 1 - 3 Years*",
        min_value=0,
        value=None,
        step=1,
        key="hcp_three_years_section",
    )

    st.markdown(
        potentiality_label,
        unsafe_allow_html=True,
    )

    potentiality = st.selectbox(
        "Choose *",
        options=["High", "Moderate", "Low"],
        index=None,
        key="hcp_potentiality",
    )

    level_of_influence = st.selectbox(
        "Level of Influence*",
        options=["High", "Moderate", "Low"],
        index=None,
        key="hcp_level_of_influence",
    )
    cycle_goals = st.selectbox(
        "Cycle Goals*", options=GOALS, index=None, key="hcp_cycle_goals"
    )
    product_px_reco = st.multiselect(
        "Product Px/RECO*", options=PRODUCTS, key="hcp_product_px_reco"
    )

    st.markdown("**required*")

    message_placeholder = st.empty()  # Empty container for success or error messages
    spinner_placeholder = st.empty()  # New empty container for spinner

    # Submit Button
    if st.button(
        "Submit Report",
        key="submit_daily_form",
        help="Submit your daily report",
        type="primary",
        icon=":material/send_money:",
        use_container_width=True,
    ):
        if not (
            selected_agent
            and selected_address
            and selected_workplace
            and department
            and prefix
            and client_name
            and colour_codes
            and adoption_ladder
            and six_months_section
            and one_year_section
            and three_years_section
            and potentiality
            and level_of_influence
            and cycle_goals
            and product_px_reco
        ):
            message_placeholder.warning("Ensure all mandatory fields are filled.")
        else:
            # Show spinner in the new location
            with spinner_placeholder:
                with st.spinner("Submitting your details..."):
                    # Collecting and submitting data
                    submission_time = current_time()

                    # Get workplace details using the composite key
                    workplace_key = f"{selected_address}_{selected_workplace}"
                    workplace_info = workplace_details.get(workplace_key, {})
                    products_str = ", ".join(product_px_reco)
                    client_name = client_name.capitalize()

                    daily_data = pd.DataFrame(
                        [
                            {
                                "TimeStamp": submission_time.strftime(
                                    "%d-%m-%Y  %H:%M:%S"
                                ),
                                "Agent": selected_agent,
                                "Territory": selected_territory,
                                "Prefix": prefix,
                                "Client_Name": client_name,
                                "Cadre": cadre,
                                "Workplace": selected_workplace,
                                "Workplace_Type": workplace_info.get(
                                    "Workplace_Type", ""
                                ),
                                "City": workplace_info.get("City", ""),
                                "Postal_Area": workplace_info.get("Postal_Area", ""),
                                "State": workplace_info.get("State", ""),
                                "Department": department,
                                "Line_Address": selected_address,
                                "Colour CODE": colour_codes,
                                "Adoption Ladder": adoption_ladder,
                                "Nb of  babies seen 0 - 6 Months": six_months_section,
                                "Nb of  babies seen 6 months - 1 Yr": one_year_section,
                                "Nb of  babies seen 1 - 3 Yrs": three_years_section,
                                "Potentiality": potentiality,
                                "Level of Influence": level_of_influence,
                                "Cycle Goals": cycle_goals,
                                "Product Px/RECO": products_str,
                            }
                        ]
                    )

                    # Append data
                    conn = st.connection("gsheets", type=GSheetsConnection)
                    existing_pending_clients_data = pd.concat(
                        [existing_pending_clients_data, daily_data], ignore_index=True
                    )
                    conn.update(
                        worksheet="PendingClients", data=existing_pending_clients_data
                    )

            # Display success
            message_placeholder.success(
                "Client Details successfully submitted!",
                icon=":material/thumb_up:",
            )
