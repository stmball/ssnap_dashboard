"""Entrypoint for the streamlit app."""

import streamlit as st

from stroke_dashboard.views import national, regional, trust

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
            st.Page(regional, title="Regional Overview"),
            st.Page(trust, title="Trust Overview"),
        ]
    }
)

pg.run()
