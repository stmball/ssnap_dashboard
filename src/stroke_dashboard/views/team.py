import streamlit as st

import pandas as pd


def map_letter_grades(grade: str):
    if len(grade) == 1:
        return -ord(grade)
    else:
        return 0


def calculate_delta(metric: str, current: str, last: str):
    if current.isnumeric() and last.isnumeric():
        return float(current) - float(last)
    else:
        return map_letter_grades(current) - map_letter_grades(last)


def team():
    list_of_regions = (
        pd.read_csv("data/overview/by_metric/summary_data_Team_SSNAP score.csv")
        .columns[1:]
        .sort_values()
    )

    st.title("SSNAP - Team Overview")

    regions = st.selectbox(
        "Select a team",
        list_of_regions,
    )

    if len(regions) == 0:
        st.write("Please select a metric to measure.")
        return

    national = pd.read_csv(
        "data/overview/by_metric/summary_data_Team_SSNAP score.csv", index_col=0
    )

    national = national.mean(axis=1)

    region_data = pd.read_csv(f"data/processed/TEAM/{regions}.csv").drop(0)
    region_data = region_data.set_index(region_data.columns[0])

    ssnap_scores = pd.to_numeric(region_data.iloc[1, :], errors="coerce")

    ssnap_scores = pd.DataFrame([ssnap_scores, national]).transpose()

    ssnap_scores.columns = [f"{regions}", "National Average"]

    st.header("SSNAP Scores for Team")
    st.line_chart(ssnap_scores)

    st.header("Most Recent Metrics (versus last period)")
    cols = st.columns(3)

    metrics = region_data.index
    current_data = region_data.iloc[:, -1].tolist()
    last_period_data = region_data.iloc[:, -2].tolist()

    for idx, (metric, current, last) in enumerate(
        zip(metrics, current_data, last_period_data)
    ):
        delta = calculate_delta(metric, current, last)
        cols[idx % 3].metric(metric, current, delta=delta)
