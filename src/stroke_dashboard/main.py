import streamlit as st
import numpy as np
import pandas as pd

from pathlib import Path


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

if len(teams) == 1:
    data = get_data(teams[0])
    st.dataframe(data)
