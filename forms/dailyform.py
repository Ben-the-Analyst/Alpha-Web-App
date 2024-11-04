import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import time
import pytz
import re


def load_form_data():
    time.sleep(2)


# Function to get current time
def current_time():
    timezone = pytz.timezone("Africa/Nairobi")  # Setting timezone to East Africa
    return datetime.now(timezone)


def validate_input(input_value):
    if input_value == "":
        return False
    else:
        return True


def validate_one_word_any_capital(input_str):
    """
    Validates that the input is a single word, allowing any combination of uppercase and lowercase letters.
    """
    pattern = r"^[A-Za-z]+$"
    return bool(re.match(pattern, input_str))


def daily_form():
    with st.spinner("Loading your form ..."):
        load_form_data()
    # Daily Activity Form
    st.write("All the fields are mandatory")

    # Establishing a Google Sheets connection
    conn = st.connection("gsheets", type=GSheetsConnection)

    # Fetch existing ner data
    existing_daily_data = conn.read(worksheet="DailyData")
    institutions_list_data = conn.read(worksheet="Institutions")
    cadre = conn.read(worksheet="Cadre")
    institution_types = conn.read(worksheet="Type")
    institutions_department = conn.read(worksheet="Department")
    outcomes = conn.read(worksheet="Outcome")

    # List of data imports from sheets
    PREFIXES = ["Mr.", "Mrs.", "Ms.", "Dr.", "Prof."]
    TERRITORIES = institutions_list_data["Territories"].unique().tolist()
    AGENTNAMES = institutions_list_data["Names"].unique().tolist()
    CADRE = cadre["Cadre"].unique().tolist()
    TYPE = institution_types["Type"].unique().tolist()
    DEPARTMENT = institutions_department["Department"].unique().tolist()
    OUTCOMES = outcomes["Outcomes"].unique().tolist()

    # sorted lists
    PREFIXES = sorted(PREFIXES)
    TERRITORIES = sorted(TERRITORIES)
    AGENTNAMES = sorted(AGENTNAMES)
    CADRE = sorted(CADRE)
    TYPE = sorted(TYPE)
    DEPARTMENT = sorted(DEPARTMENT)
    OUTCOMES = sorted(OUTCOMES)

    # Onboarding New Daily Activity Form
    with st.form(key="daily_form", clear_on_submit=True):
        agentname = st.selectbox(
            "Your Name*", options=AGENTNAMES, index=None, key="daily_agentname"
        )
        territories = st.selectbox(
            "Territory*", options=TERRITORIES, index=None, key="daily_territories"
        )
        date = st.date_input(label="Date", format="DD/MM/YYYY", key="daily_date")
        prefix = st.selectbox(
            "prefix*", options=PREFIXES, index=None, key="daily_prefix"
        )
        client_surname = st.text_input(
            label="HCP/Client Surname*", key="daily_client_surname"
        )
        client_firstname = st.text_input(
            label="HCP/Client Firstname*", key="daily_client_firstname"
        )
        cadre = st.selectbox("Cadre*", options=CADRE, index=None, key="daily_cadre")
        pos_type = st.selectbox(
            "Institution (POS) Type*", options=TYPE, index=None, key="daily_pos_type"
        )
        department = st.selectbox(
            "Institution Department*",
            options=DEPARTMENT,
            index=None,
            key="daily_department",
        )
        objective = st.text_input(label="Task Objective*", key="daily_objective")
        comments = st.text_area(label="Comments/Notes*", key="daily_comments")
        outcomes = st.selectbox(
            "Overall Outcome*",
            options=OUTCOMES,
            index=None,
            key="daily_outcomes",
            placeholder="Choose most relevant ",
        )
        future_objective = st.text_area(
            label="Future Task Objective", key="daily_future_objective"
        )
        appointment = st.date_input(
            label="Next Appointment", format="DD/MM/YYYY", key="daily_appointment"
        )

        # territories = st.selectbox("Territory*", options=TERRITORIES, index=None)
        # date = st.date_input(label="Date", format="DD/MM/YYYY")
        # prefix = st.selectbox("prefix*", options=PREFIXES, index=None)
        # client_surname = st.text_input(label="HCP/Client Surname*")
        # client_firstname = st.text_input(label="HCP/Client Firstname*")
        # cadre = st.selectbox("Cadre*", options=CADRE, index=None)
        # pos_type = st.selectbox("Institution (POS) Type*", options=TYPE, index=None)
        # department = st.selectbox(
        #     "Institution Department*", options=DEPARTMENT, index=None
        # )
        # objective = st.text_input(label="Task Objective*")
        # comments = st.text_area(label="Comments/Notes*")
        # future_objective = st.text_area(label="Future Task Objective")
        # appointment = st.date_input(label="Next Appointment", format="DD/MM/YYYY")

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
            if not validate_one_word_any_capital(client_surname):
                st.error("Client Surname must be a single word.")
                st.stop()
            if not validate_one_word_any_capital(client_firstname):
                st.error("Client Firstname must be a single word.")
                st.stop()
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
                or not outcomes
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
                # Show spinner while processing
                with st.spinner("Submitting your details..."):
                    # Simulate processing time
                    load_form_data()
                # Get the current time at submission
                submission_time = current_time()

                # Capitalize the first letter of each field
                client_surname = client_surname.capitalize()
                client_firstname = client_firstname.capitalize()
                objective = objective.capitalize()
                comments = comments.capitalize()
                future_objective = future_objective.capitalize()

                # Create a new row of   data
                daily_data = pd.DataFrame(
                    [
                        {
                            "Name": agentname,
                            "Territory": territories,
                            "Date": date.strftime("%d-%m-%Y"),
                            "Prefix": prefix,
                            "HCP Surname": client_surname,
                            "HCP Firstname": client_firstname,
                            "Cadre": cadre,
                            "Institution (POS) Type": pos_type,
                            "Institution Department": department,
                            "Task Objective": objective,
                            "Comments/Notes": comments,
                            "Outcome": outcomes,
                            "Future Task Objective": future_objective,
                            "Next Appointment": appointment.strftime("%d-%m-%Y"),
                            "TimeStamp": submission_time.strftime("%d-%m-%Y  %H:%M:%S"),
                        }
                    ]
                )

                # Add the new   data to the existing data
                updated_daily_df = pd.concat(
                    [existing_daily_data, daily_data], ignore_index=True
                )

                # Update Google Sheets with the new   data
                conn.update(worksheet="DailyData", data=updated_daily_df)

                st.success(
                    icon=":material/thumb_up:",
                    body="Daily Activity details successfully submitted!",
                )
