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
    product_px_reco = conn.read(worksheet="Competitors")
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


# --------------------GENERATE CLIENT ID---------------------------------------------------------------
def generate_client_id(conn):
    """
    Generates a unique client ID in the format AP/CL/YYMM/XXXX
    where XXXX is an incremental number that resets each month
    """
    current_date = datetime.now()
    current_ym = current_date.strftime("%y%m")

    # Fetch only the Client_ID column directly from the database
    latest_ids = conn.read(worksheet="ClientsDatabase", usecols=["Client_ID"])

    # Filter existing IDs for the current month
    pattern = f"AP/CL/{current_ym}/\\d{{4}}"
    current_month_ids = latest_ids[
        latest_ids["Client_ID"].str.match(pattern, na=False)
    ]["Client_ID"].tolist()

    if not current_month_ids:
        next_number = 1
    else:
        numbers = [int(id.split("/")[-1]) for id in current_month_ids]
        next_number = max(numbers) + 1

    new_id = f"AP/CL/{current_ym}/{next_number:04d}"
    return new_id


# --------------------DAILY REPORTING FORM---------------------------------------------------------------
def clear_form():
    """Clears the form input fields."""
    st.session_state["new_hcp_prefix"] = ""
    st.session_state["new_hcp_client_name"] = ""
    st.session_state["new_hcp_workplace"] = ""
    st.session_state["new_hcp_workplace_type"] = None
    st.session_state["new_hcp_department"] = None
    st.session_state["new_hcp_cadre"] = None
    st.session_state["new_hcp_line_address"] = ""
    st.session_state["new_hcp_city"] = ""
    st.session_state["new_hcp_postal_area"] = ""
    st.session_state["new_hcp_state"] = ""
    st.session_state["new_hcp_colour_codes"] = None
    st.session_state["new_hcp_adoption_ladder"] = 0
    st.session_state["new_hcp_six_months_section"] = 0
    st.session_state["new_hcp_one_year_section"] = 0
    st.session_state["new_hcp_three_years_section"] = 0
    st.session_state["new_hcp_potentiality"] = None
    st.session_state["new_hcp_level_of_influence"] = None
    st.session_state["new_hcp_cycle_goals"] = None
    st.session_state["new_hcp_product_px_reco"] = []


def hcp_form_new_client():

    st.write("For New Client in a New Workplace in a New Address")

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
    PRODUCTS = product_px_reco["Competitors"].unique().tolist()

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

    prefix = st.selectbox(
        label="Prefix",
        options=PREFIXES,
        key="hcp_prefix",
        index=None,
    )

    client_name = st.text_input(
        label="HCP/Client/Retailer Name: (Firstname Surname)*",
        key="new_hcp_client_name",
        placeholder="e.g. John Doe",
    )

    cadre = st.selectbox(
        label="Cadre",
        options=CADRE,
        key="new_hcp_cadre",
        index=None,
    )

    workplace = st.text_input(
        label="Workplace*",
        key="new_hcp_workplace",
        placeholder="e.g. Hospital Name",
    )

    workplace_type = st.selectbox(
        label="Workplace Type*",
        options=TYPE,
        key="new_hcp_workplace_type",
        placeholder="e.g. Hospital",
        index=None,
    )

    department = st.selectbox(
        label="Department",
        options=DEPARTMENT,
        key="new_hcp_department",
        index=None,
        placeholder="e.g. Pharmacy",
    )

    line_address = st.text_input(
        label="Line Address*",
        placeholder="e.g. Main Street",
        key="new_hcp_line_address",
    )

    postal_area = st.text_input(
        label="Postal Area*",
        placeholder="e.g. Kilimani",
        key="new_hcp_postal_area",
    )

    city = st.text_input(
        label="City*",
        placeholder="e.g. Nairobi",
        key="new_hcp_city",
    )

    state = st.text_input(
        label="State*",
        placeholder="e.g. Nairobi County-Embakasi East",
        key="new_hcp_state",
    )

    colour_codes = st.selectbox(
        label="Colour CODE*",
        options=COLORCODES,
        key="new_hcp_colour_codes",
        index=None,
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
        key="new_hcp_adoption_ladder",
    )

    with st.expander("SECTION: REACH", icon=":material/view_cozy:", expanded=True):
        st.markdown(section_label)
        six_months_section = st.number_input(
            label="Number of babies seen in 0 - 6 Months",
            value=None,
            step=1,
            key="new_hcp_six_months_section",
        )

        one_year_section = st.number_input(
            label="Number of babies seen in 6 months - 1 Year",
            value=None,
            step=1,
            key="new_hcp_one_year_section",
        )

        three_years_section = st.number_input(
            label="Number of babies seen in 1 - 3 Years",
            value=None,
            step=1,
            key="new_hcp_three_years_section",
        )

        st.markdown(
            potentiality_label,
            unsafe_allow_html=True,
        )

        potentiality = st.selectbox(
            "Choose potentiality",
            options=["High", "Moderate", "Low"],
            index=None,
            key="new_hcp_potentiality",
        )

    level_of_influence = st.selectbox(
        "Level of Influence*",
        options=["High", "Moderate", "Low"],
        index=None,
        key="new_hcp_level_of_influence",
    )
    cycle_goals = st.selectbox(
        "Cycle Goals*", options=GOALS, index=None, key="new_hcp_cycle_goals"
    )
    product_px_reco = st.multiselect(
        label="Product Px/RECO*",
        options=PRODUCTS,
        key="new_hcp_product_px_reco",
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
            workplace
            and city
            and postal_area
            and state
            and client_name
            and cadre
            and department
            and prefix
            and workplace_type
            and line_address
            and colour_codes
            and adoption_ladder
            and level_of_influence
            and cycle_goals
            and product_px_reco
        ):
            message_placeholder.error("Ensure all mandatory fields are filled.")
            st.stop()

        # Convert inputs to lowercase for case-insensitive comparison
        workplace_lower = workplace.lower().strip()
        client_name_lower = client_name.lower().strip()
        line_address_lower = line_address.lower().strip()

        # Get fresh data from database for validation
        conn = st.connection("gsheets", type=GSheetsConnection)
        live_clients_data = conn.read(
            worksheet="ClientsDatabase",
            usecols=["Workplace", "Line_Address", "Client_Name"],
        )

        if (
            live_clients_data["Workplace"].str.lower().str.strip() == workplace_lower
        ).any():
            message_placeholder.warning("A workplace with this name already exists.")
            st.stop()
        elif (
            live_clients_data["Line_Address"].str.lower().str.strip()
            == line_address_lower
        ).any():
            message_placeholder.warning("An address with this name already exists.")
            st.stop()
        elif (
            live_clients_data["Client_Name"].str.lower().str.strip()
            == client_name_lower
        ).any():
            message_placeholder.warning("A client with this name already exists.")
            st.stop()

        else:
            # Show spinner in the new location
            with spinner_placeholder:
                with st.spinner("Submitting your details..."):
                    # Collecting and submitting data
                    submission_time = current_time()

                    conn = st.connection("gsheets", type=GSheetsConnection)
                    new_client_id = generate_client_id(conn)

                    products_str = ", ".join(product_px_reco)

                    # Normalize string inputs to title case
                    client_name = client_name.strip().title()
                    workplace = workplace.strip().title()
                    line_address = line_address.strip().title()
                    city = city.strip().title()
                    postal_area = postal_area.strip().title()
                    state = state.strip().title()

                    data = pd.DataFrame(
                        [
                            {
                                "TimeStamp": submission_time.strftime(
                                    "%d-%m-%Y  %H:%M:%S"
                                ),
                                "Agent": selected_agent,
                                "Territory": selected_territory,
                                "Client_ID": new_client_id,
                                "Prefix": prefix,
                                "Client_Name": client_name,
                                "Cadre": cadre,
                                "Workplace": workplace,
                                "Workplace_Type": workplace_type,
                                "City": city,
                                "Postal_Area": postal_area,
                                "State": state,
                                "Department": department,
                                "Line_Address": line_address,
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
                    clients_list_data = pd.concat(
                        [clients_list_data, data], ignore_index=True
                    )
                    conn.update(worksheet="ClientsDatabase", data=clients_list_data)

            # Display success message with the new client ID
            message_placeholder.success(
                f"Client Details successfully submitted! Client ID: {new_client_id}",
                icon=":material/thumb_up:",
            )
            
            st.cache_data.clear()
