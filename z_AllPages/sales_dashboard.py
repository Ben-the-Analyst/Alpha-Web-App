import json
import streamlit as st
import pandas as pd
import os
from pathlib import Path
from streamlit_gsheets import GSheetsConnection


# create a connection to the Google Sheet
conn = st.connection("gsheets", type=GSheetsConnection)
settings_list_data = conn.read(worksheet="Settings")


@st.cache_data(ttl=300)
def load_route_data():
    return conn.read(worksheet="RoutePlanner")


# AGENTNAMES = sorted(settings_list_data["Names"].unique().tolist())
# REGIONS = sorted(settings_list_data["Regions"].unique().tolist())
# INSTITUTIONS = sorted(settings_list_data["Institutions"].unique().tolist())
import pandas as pd
import streamlit as st
import json

# Assuming settings_list_data is your DataFrame with the required columns
# Example DataFrame creation (you would replace this with your actual data loading)
# settings_list_data = pd.DataFrame({
#     "Names": ["Agent1", "Agent2", "Agent1", "Agent3"],
#     "Regions": ["Africa", "Africa", "Asia", "Asia"],
#     "Institutions": ["Algeria", "Angola", "China", "India"]
# })


@st.cache_data(persist=True)
def build_hierarchical_data(df):
    # Build the hierarchical structure
    cached_data = {}

    for _, row in df.iterrows():
        agent_name = row["Names"]
        region = row["Regions"]
        institution = row["Institutions"]

        # Create nested dictionaries as needed
        if agent_name not in cached_data:
            cached_data[agent_name] = {}  # Start a new dictionary for the agent

        if region not in cached_data[agent_name]:
            cached_data[agent_name][region] = []  # Start a new list for the region

        # Add institution to the agent's region
        if institution not in cached_data[agent_name][region]:
            cached_data[agent_name][region].append(institution)

    # Sort the keys alphabetically for better organization
    for agent in cached_data:
        for region in cached_data[agent]:
            cached_data[agent][region] = sorted(
                cached_data[agent][region]
            )  # Sort institutions

    # Sort the outer keys (agents)
    cached_data = {k: cached_data[k] for k in sorted(cached_data)}

    return cached_data

# Build and cache the hierarchical data
cached_data = build_hierarchical_data(settings_list_data)

# # Display the hierarchical data in the app
# st.json(cached_data)


BASE_PATH = "."


@st.cache_data(persist=True)
def load_locations():
    with open(f"{BASE_PATH}/z-global-locations.json", "rt", encoding="utf8") as f:
        locations_str = f.read()
    locations_json = json.loads(locations_str)
    return locations_json


locations = load_locations()
# Create tabs for different forms
tab = st.tabs(["Route Planner Form", "Daily Reporting Form", "HCP Form"])

# Route Planner Form Tab
with tab[0]:
    c1, _, c3 = st.columns([3, 1, 4])
    with c1:
        st.subheader("Locations data")
        st.json(locations, expanded=False)
    with c3:
        st.subheader("Cascade selections")
        region = st.selectbox("Select region", options=locations.keys())
        country = st.selectbox("Select country", options=locations[region].keys())
        cities = st.multiselect("Select city", options=locations[region][country])

with tab[1]:
    st.subheader("Dependent data Data Filtering")
    agentname = st.selectbox("Select Name", options=cached_data.keys())
    region = st.selectbox("Select Region", options=cached_data[agentName].keys())
    institutions = st.multiselect(
        "Select Institutions / Stores", options=cached_data[agentName][regions]
    )


with tab[2]:
    st.subheader("Some content here")
