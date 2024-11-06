import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import time
import pytz
import re


def load_form_data():
    time.sleep(4)


# Function to get current time
def current_time():
    timezone = pytz.timezone("Africa/Nairobi")  # Setting timezone to East Africa
    return datetime.now(timezone)


def validate_one_word_any_capital(input_str):
    """
    Validates that the input is a single word, allowing any combination of uppercase and lowercase letters.
    """
    pattern = r"^[A-Za-z]+$"
    return bool(re.match(pattern, input_str))


def validate_positive_number(input_str):
    """
    Validates that the input is a positive number.
    """
    try:
        number = float(input_str)
        return number > 0
    except ValueError:
        return False


def validate_whole_number_0_to_10(input_str):
    """
    Validates that the input is a whole number between 0 and 10 (inclusive).
    """
    pattern = r"^(?:[0-9]|10)$"
    return bool(re.match(pattern, input_str))


def hcp_form():
    # HCP form
    with st.spinner("Loading your form ..."):
        load_form_data()
    st.write("All the fields are mandatory")

    # Establishing a Google Sheets connection
    conn = st.connection("gsheets", type=GSheetsConnection)

    # Fetch existing data
    existing_hcp_data = conn.read(worksheet="HCPData")
    institutions_list_data = conn.read(worksheet="Institutions")
    cadre = conn.read(worksheet="Cadre")
    institution_types = conn.read(worksheet="Type")
    institutions_department = conn.read(worksheet="Department")
    cycle_goals = conn.read(worksheet="Cycle_Goals")
    product_px_reco = conn.read(worksheet="Products")

    # List of data imports from sheets
    PREFIXES = ["Mr.", "Mrs.", "Ms.", "Dr.", "Prof."]
    COLORCODES = ["RED", "BLUE", "GREEN", "YELLOW"]
    TERRITORIES = institutions_list_data["Territories"].unique().tolist()
    AGENTNAMES = institutions_list_data["Names"].unique().tolist()
    CADRE = cadre["Cadre"].unique().tolist()
    TYPE = institution_types["Type"].unique().tolist()
    DEPARTMENT = institutions_department["Department"].unique().tolist()
    GOALS = cycle_goals["Cycle_Goals"].unique().tolist()
    PRODUCTS = product_px_reco["Products"].unique().tolist()

    # Sorted lists
    PREFIXES = sorted(PREFIXES)
    COLORCODES = sorted(COLORCODES)
    TERRITORIES = sorted(TERRITORIES)
    AGENTNAMES = sorted(AGENTNAMES)
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

    def validate_fields():
        if not validate_one_word_any_capital(client_surname):
            message_placeholder.error("Client Surname must be a single word.")
            st.stop()
        if not validate_one_word_any_capital(client_firstname):
            message_placeholder.error("Client Firstname must be a single word.")
            st.stop()

    # Onboarding New HCP Activity Form

    with st.form(key="hcp_form", clear_on_submit=True):
        agentname = st.selectbox(
            "Your Name*", options=AGENTNAMES, index=None, key="hcp_agentname"
        )
        if agentname:
            territory = institutions_list_data[
                institutions_list_data["Names"] == agentname
            ]["Territories"].iloc[0]
        else:
            territory = None
        institution = st.text_input(label="Institution Name*", key="hcp_institution")
        pos_type = st.selectbox(
            "Institution (POS) Type*", options=TYPE, index=None, key="hcp_pos_type"
        )
        department = st.selectbox(
            "Institution Department*",
            options=DEPARTMENT,
            index=None,
            key="hcp_department",
        )
        prefix = st.selectbox("prefix*", options=PREFIXES, index=None, key="hcp_prefix")
        client_surname = st.text_input(
            label="HCP/Client Surname*", key="hcp_client_surname"
        )
        client_firstname = st.text_input(
            label="HCP/Client Firstname*", key="hcp_client_firstname"
        )
        cadre = st.selectbox("Cadre*", options=CADRE, index=None, key="hcp_cadre")
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
        st.markdown(section_label)
        six_months_section = st.number_input(
            label="0 - 6 Months*",
            min_value=0,
            value=None,
            step=1,
            key="hcp_six_months_section",
        )
        one_year_section = st.number_input(
            label="6 months - 1 Year*",
            min_value=0,
            value=None,
            step=1,
            key="hcp_one_year_section",
        )
        three_years_section = st.number_input(
            label="1 - 3 Years*",
            min_value=0,
            value=None,
            step=1,
            key="hcp_three_years_section",
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
        product_px_reco = st.selectbox(
            "Product Px/RECO*", options=PRODUCTS, index=None, key="hcp_product_px_reco"
        )

        # Mark mandatory fields
        st.markdown("**required*")

        message_placeholder = (
            st.empty()
        )  # Empty container for success or error messages
        spinner_placeholder = st.empty()  # New empty container for spinner
        st.divider()

        # i need the spinner here

        submit_button = st.form_submit_button(
            label="Submit ",
            help="Submit your Details",
            type="primary",
            icon=":material/send_money:",
            use_container_width=True,
        )

        # If the submit button is pressed
        if submit_button:
            validate_fields()
            # Required fields to ensure all are filled
            required_fields = [
                agentname,
                territory,
                institution,
                pos_type,
                department,
                prefix,
                client_surname,
                client_firstname,
                cadre,
                colour_codes,
                adoption_ladder,
                potentiality,
                six_months_section,
                one_year_section,
                three_years_section,
                level_of_influence,
                cycle_goals,
                product_px_reco,
            ]

            # Check all required fields are filled
            if any(not field for field in required_fields):
                message_placeholder.warning(
                    icon=":material/error:",
                    body="Ensure all fields are filled.",
                )
                st.stop()
            else:
                with spinner_placeholder:
                    with st.spinner(
                        "Submitting your details..."
                    ):  # Show spinner while processing
                        # load_form_data() # # Simulate processing time

                        submission_time = (
                            current_time()
                        )  # Get the current time at submission
                        institution = institution.capitalize()
                        client_surname = client_surname.capitalize()
                        client_firstname = client_firstname.capitalize()
                        # Create a new row of HCP data
                        hcp_data = pd.DataFrame(
                            [
                                {
                                    "Name": agentname,
                                    "Territory": territory,
                                    "Institution Name": institution,
                                    "Institution (POS) Type": pos_type,
                                    "Institution Department": department,
                                    "Prefix": prefix,
                                    "HCP/Client Surname	": client_surname,
                                    "HCP/Client First Name": client_firstname,
                                    "Cadre": cadre,
                                    "Colour CODE": colour_codes,
                                    "Adoption Ladder": adoption_ladder,
                                    "Potentiality": potentiality,
                                    "0 - 6 Months": six_months_section,
                                    "6 months - 1 Year": one_year_section,
                                    "1 - 3 Years": three_years_section,
                                    "Level of Influence": level_of_influence,
                                    "Cycle Goals": cycle_goals,
                                    "Product Px/RECO": product_px_reco,
                                    "TimeStamp": submission_time.strftime(
                                        "%d-%m-%Y  %H:%M:%S"
                                    ),
                                }
                            ]
                        )

                        # Add the new HCP data to the existing data
                        updated_hcp_df = pd.concat(
                            [existing_hcp_data, hcp_data], ignore_index=True
                        )

                        # Update Google Sheets with the new  data
                        conn.update(worksheet="HCPData", data=updated_hcp_df)

                        message_placeholder.success(
                            icon=":material/thumb_up:",
                            body="HCP details successfully submitted!",
                        )
