import streamlit as st
import numpy as np
import pandas as pd

from pathlib import Path


def color_scale(val):
    if isinstance(val, str):
        if val == "E":
            return "background-color: black"
        elif val == "D":
            return "background-color: red"
        elif val == "C":
            return "background-color: orange"
        elif val == "B":
            return "background-color: yellow"
        elif val == "A":
            return "background-color: green"


def get_data(team: str):
    import_path = Path("data") / "processed" / f"{team}.csv"
    df = pd.read_csv(import_path, index_col=0)
    return df


# Streamlit config options
st.set_page_config(
    page_title="SSNAP Dashboard",
    page_icon=":bar_chart:",
    layout="wide",
    initial_sidebar_state="expanded",
)

df = pd.read_csv("data/data.csv", index_col=0)

teams = df.columns
df = df.melt(ignore_index=False).reset_index()
df.columns = ["Quarter", "Team", "Score"]
df["Score"] = df["Score"].replace(".", np.nan).astype(float)
df.dropna(inplace=True)


st.title("SSNAP Dashboard")

teams = st.multiselect("Select teams", teams)

st.text(
    "This dashboard shows the current SSNAP gradings, tracked over time. Note that some data may be missing due to parsing/reporting errors."
)

df = df[df["Team"].isin(teams)]
latest_scores = df.groupby("Quarter").mean(numeric_only=True)


if teams:
    top_col_1, top_col_2 = st.columns([0.7, 0.3])
    top_col_1.line_chart(
        df, x="Quarter", y="Score", color="Team", use_container_width=True
    )
    top_col_2.metric(
        "Current score across selected teams",
        f"{latest_scores.iloc[-1, 0]:.2f}",
        f"{latest_scores.iloc[-1, 0] - latest_scores.iloc[-2, 0]:.2f}",
    )

    for team in teams:
        data = get_data(team)

        # Color boxes based on score scaled
        st.header(f"Data Breakdown for {team}")
        st.dataframe(data.style.applymap(color_scale))
