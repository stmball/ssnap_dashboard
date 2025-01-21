"""View for the national statistics
- Aimed for policy makers/manages at a national, holistic level.
- Provides an overview of the national statistics.
- Can be used to compare regions and trusts.
"""

import streamlit as st
import pandas as pd

from pathlib import Path


def get_available_metrics():
    available_metrics = {
        a.stem.split("_")[3]
        for a in list(Path("data/overview/by_metric").glob("*.csv"))
    }
    return available_metrics


def load_metric_data(level: str, option: str):
    datapath = Path("data/overview/by_metric") / f"summary_data_{level}_{option}.csv"
    data = pd.read_csv(datapath, index_col=0)
    return data


def handle_level_change():
    level = st.session_state.pill


def national():
    st.title("SSNAP - National Overview")
    st.write(
        "This is the national overview page, comparing all the regions nationally. Here you can see what the overall national SSNAP score is over time, and the biggest improvers/decliners on the last quarter.."
    )
    available_metrics = get_available_metrics()

    # options = st.multiselect(
    #     "Select a metric to measure",
    #     available_metrics,
    #     max_selections=1,
    # )
    #
    # if len(options) == 0:
    #     st.write("Please select a metric to measure.")
    #     return

    options = [
        "SSNAP Score",
    ]
    data = load_metric_data("ISDN", options[0])
    mean_scores = data.mean(axis=1)

    # Line chart of mean score per year.
    st.header(f"Mean {options[0]} Score per Year")
    st.line_chart(mean_scores, x_label="Year", y_label=f"Mean {options[0]} Score")

    # Display the mean scores for the most recent quarter.
    segemented_control = st.segmented_control(
        "Level",
        ["ISDN", "Trust", "Team"],
        default="ISDN",
    )

    data = load_metric_data(segemented_control, options[0])

    col1, col2 = st.columns(2, vertical_alignment="center")

    this_quarter = data.iloc[-1, :].mean(axis=0)
    quarter_difference = this_quarter - data.iloc[-2, :].mean(axis=0)

    col1.metric("This Quarter", f"{this_quarter:.2f}", f"{quarter_difference:.2f}")

    this_year = data.iloc[:, -4:].mean().mean()
    last_year = data.iloc[:, -8:-4].mean().mean()
    year_difference = this_year - last_year

    col2.metric("This Year", f"{this_year:.2f}", f"{year_difference:.2f}")

    col1.header("Top 5 This Quarter")
    col1.dataframe(data.iloc[-1, :].nlargest(5), use_container_width=True)

    col2.header("Bottom 5 This Quarter")
    col2.dataframe(data.iloc[-1, :].nsmallest(5), use_container_width=True)

    col1.header("Improvers This Quarter")
    col1.dataframe(
        data.diff()
        .iloc[-1, :]
        .nlargest(5)
        .to_frame()
        .style.applymap(lambda x: "color: green"),
        use_container_width=True,
    )

    col2.header("Decliners This Quarter")
    col2.dataframe(
        data.diff()
        .iloc[-1, :]
        .nsmallest(5)
        .to_frame()
        .style.format("{:.2f}")
        .applymap(lambda x: "color: red"),
        use_container_width=True,
    )
