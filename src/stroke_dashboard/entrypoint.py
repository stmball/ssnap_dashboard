"""Entrypoint for the streamlit app."""

import streamlit as st
from pathlib import Path

from stroke_dashboard.views import national, trust, team, isdn
from stroke_dashboard.parsing import process_data

data_path = Path("data/processed/TEAM/")

if not data_path.exists():
    process_data()

st.set_page_config(
    page_title="SSNAP Stroke Dashboard",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

pg = st.navigation(
    {
        "Views": [
            st.Page(national, title="National Overview"),
            st.Page(isdn, title="ISDN Overview"),
            st.Page(trust, title="Trust Overview"),
            st.Page(team, title="Team Overview"),
        ]
    }
)

pg.run()
