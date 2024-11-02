import json
import streamlit as st
import pandas as pd
import os
from pathlib import Path

# Create tabs for different forms
tab = st.tabs(["Dashboard1", "Dashboard2", "Dashboard3"])

# Route Planner Form Tab
with tab[0]:
    st.subheader("Some content here")

with tab[1]:
    st.subheader("Some content here")

with tab[2]:
    st.subheader("Some content here")
