import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import time


def load_form_data():
    time.sleep(2)


# Function to get current time
def current_time():
    return datetime.now().time()


def hcp_form():
    # HCP form
    with st.spinner("Loading your form ..."):
        load_form_data()
    st.write("All the fields are mandatory")

    # Establishing a Google Sheets connection
    conn = st.connection("gsheets", type=GSheetsConnection)

    # Fetch existing data
    settings_list_data = conn.read(worksheet="Settings")
    existing_hcp_data = conn.read(worksheet="HCPData")

    # List of data imports from sheets
    TERRITORIES = settings_list_data["Territories"].unique().tolist()
    AGENTNAMES = settings_list_data["Names"].unique().tolist()
    PREFIXES = settings_list_data["Prefixes"].unique().tolist()
    CADRE = settings_list_data["Cadre"].unique().tolist()
    TYPE = settings_list_data["Type"].unique().tolist()
    DEPARTMENT = settings_list_data["Department"].unique().tolist()
    COLORCODES = settings_list_data["Colour_CODE"].unique().tolist()
    GOALS = settings_list_data["Cycle_Goals"].unique().tolist()
    PRODUCTS = settings_list_data["Products"].unique().tolist()

    # Labels with HTML formatting for font size control
    adoption_ladder_label = """
        <p>Adoption Ladder</p>
        <ul style="font-size: 0.2em; color: gray;">
            <li><b>0-2</b>: RED</li>
            <li><b>3-6</b>: GREEN</li>
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

    # Onboarding New HCP Activity Form
    with st.form(key="hcp_form", clear_on_submit=True):
        agentname = st.selectbox(
            "Your Name*", options=AGENTNAMES, index=None, key="hcp_agentname"
        )
        territories = st.selectbox(
            "Territory*", options=TERRITORIES, index=None, key="hcp_territories"
        )
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
        adoption_ladder = st.text_input(
            label="Pick a number between 0 and 10*", key="hcp_adoption_ladder"
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
        six_months_section = st.text_input(
            label="0 - 6 Months*", key="hcp_six_months_section"
        )
        one_year_section = st.text_input(
            label="6 months - 1 Year*", key="hcp_one_year_section"
        )
        three_years_section = st.text_input(
            label="1 - 3 Years*", key="hcp_three_years_section"
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

        # territories = st.selectbox("Territory*", options=TERRITORIES, index=None)
        # institution = st.text_input(label="Institution Name*")
        # pos_type = st.selectbox("Institution (POS) Type*", options=TYPE, index=None)
        # department = st.selectbox(
        #     "Institution Department*", options=DEPARTMENT, index=None
        # )
        # prefix = st.selectbox("prefix*", options=PREFIXES, index=None)
        # client_surname = st.text_input(label="HCP/Client Surname*")
        # client_firstname = st.text_input(label="HCP/Client Firstname*")
        # cadre = st.selectbox("Cadre*", options=CADRE, index=None)
        # colour_codes = st.selectbox("Colour CODE*", options=COLORCODES, index=None)
        # st.markdown(adoption_ladder_label, unsafe_allow_html=True)
        # adoption_ladder = st.text_input(label="Pick a number between 0 and 10*")
        # st.markdown(potentiality_label, unsafe_allow_html=True)
        # potentiality = st.selectbox(
        #     "Choose *", options=["High", "Moderate", "Low"], index=None
        # )
        # st.markdown(section_label)
        # six_months_section = st.text_input(label="0 - 6 Months*")
        # one_year_section = st.text_input(label="6 months - 1 Year*")
        # three_years_section = st.text_input(label="1 - 3 Years*")
        # level_of_influence = st.selectbox(
        #     "Level of Influence*", options=["High", "Moderate", "Low"], index=None
        # )
        # cycle_goals = st.selectbox("Cycle Goals*", options=GOALS, index=None)
        # product_px_reco = st.selectbox("Product Px/RECO*", options=PRODUCTS, index=None)

        # Mark mandatory fields
        st.markdown("**required*")

        submit_button = st.form_submit_button(
            label="Submit ",
            help="Submit your Details",
            type="primary",
            icon=":material/send_money:",
            use_container_width=True,
        )

        # If the submit button is pressed
        if submit_button:
            # Check if all mandatory fields are filled
            if (
                not agentname
                or not territories
                or not institution
                or not pos_type
                or not department
                or not prefix
                or not client_surname
                or not client_firstname
                or not cadre
                or not colour_codes
                or not adoption_ladder
                or not potentiality
                or not six_months_section
                or not one_year_section
                or not three_years_section
                or not level_of_influence
                or not cycle_goals
                or not product_px_reco
            ):
                st.warning(
                    icon=":material/error:",
                    body="Ensure all fields are filled.",
                )
                st.stop()
            # elif
            else:
                # Show spinner while processing
                with st.spinner("Submitting your details..."):
                    # Simulate processing time
                    load_form_data()
                # Get the current time at submission
                submission_time = current_time()
                # Create a new row of HCP data
                hcp_data = pd.DataFrame(
                    [
                        {
                            "Name": agentname,
                            "Territory": territories,
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
                            "TimeStamp": submission_time.strftime("%d-%m-%Y  %H:%M:%S"),
                        }
                    ]
                )

                # Add the new HCP data to the existing data
                updated_hcp_df = pd.concat(
                    [existing_hcp_data, hcp_data], ignore_index=True
                )

                # Update Google Sheets with the new  data
                conn.update(worksheet="HCPData", data=updated_hcp_df)

                st.success(
                    icon=":material/thumb_up:",
                    body="HCP details successfully submitted!",
                )
