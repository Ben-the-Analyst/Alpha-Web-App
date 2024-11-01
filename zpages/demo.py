import json
import streamlit as st
import pandas as pd
import os
from pathlib import Path

st.set_page_config(page_title="Cascade Selection", layout="centered", page_icon="🌴")

BASE_PATH = "."


@st.cache_data(persist=True)
def load_locations():
    with open(f"{BASE_PATH}/z-global-locations.json", "rt", encoding="utf8") as f:
        locations_str = f.read()
    locations_json = json.loads(locations_str)
    return locations_json


locations = load_locations()

c1, _, c3 = st.columns([3, 1, 4])
with c1:
    st.subheader("Locations data")
    st.json(locations, expanded=False)
with c3:
    st.subheader("Cascade selections")
    region = st.selectbox("Select region", options=locations.keys())
    country = st.selectbox("Select country", options=locations[region].keys())
    cities = st.multiselect("Select city", options=locations[region][country])
