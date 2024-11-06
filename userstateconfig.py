import streamlit as st
from streamlit_gsheets import GSheetsConnection

# Establish a connection to Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)
users_df = conn.read(worksheet="Users")
# Extract user information from the Google Sheets data
users = users_df.to_dict("records")
fullname = []
emails = []
usernames = []
passwords = []
role = []
Territory_ID = []

# Organize user details into separate lists
for user in users:
    fullname.append(user["name"])
    emails.append(user["email"])
    usernames.append(user["username"])
    passwords.append(user["password"])
    role.append(user["role"])
    Territory_ID.append(user["Territory_ID"])


# Define the credentials dictionary in the format expected by streamlit_authenticator
credentials = {"usernames": {}}
for index in range(len(usernames)):
    credentials["usernames"][usernames[index]] = {
        "fullname": fullname[index],
        "name": usernames[index],
        "email": emails[index],
        "password": passwords[index],
        "role": role[index],
        "Territory_ID": Territory_ID[index],
    }
