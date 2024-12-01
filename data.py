from streamlit_gsheets import GSheetsConnection
import streamlit as st

# --------------------LOAD USER DATA FROM GOOGLE SHEETS---------------------------------------------------------------
conn = st.connection("gsheets", type=GSheetsConnection)
users_df = conn.read(worksheet="Users")
users = users_df.to_dict("records")

credentials = {"usernames": {}}
for user in users:
    credentials["usernames"][user["username"]] = {
        "fullname": user["name"],
        "name": user["username"],
        "email": user["email"],
        "password": user["password"],
        "role": user["role"],
        "Territory_ID": user["Territory_ID"],
    }
# --------------------LOAD DATA---------------------------------------------------------------
@st.cache_data(ttl=300)
def load_route_data():
    data = conn.read(worksheet="RoutePlan")
    return data

@st.fragment(run_every=3600)
@st.cache_data(ttl=3598)
def load_daily_data():
    return conn.read(worksheet="DailyReport")

@st.cache_data(ttl=300)
def load_hcp_clients_data():
    return conn.read(worksheet="ClientsDatabase")

@st.cache_data(ttl=300)
def load_institution_data():
    return conn.read(worksheet="InstitutionsReport")

@st.cache_data(ttl=300)
def load_pending_clients_data():
    return conn.read(worksheet="PendingClients")