"""Module for fetching data from the SSNAP website"""

import io
from datetime import datetime
from enum import Enum
from pathlib import Path

import pandas as pd
import requests


class Quarters(Enum):
    """Enum for the quarters of the year"""

    Q1 = "JanMar"
    Q2 = "AprJun"
    Q3 = "JulSep"
    Q4 = "OctDec"


def get_quarters():
    """Get all quarters from Q3 2013 to present day

    Note that the data is only available from Q3 2013 onwards, and some data may be
    missing for some quarters.

    Returns: list of strings for each quarter.
    """

    quarters = []
    for year in range(2013, datetime.now().year + 1):
        for quarter in Quarters:
            quarters.append(f"{quarter.value}{year}")

    return quarters


def fetch_summary_data(quarter: str) -> pd.DataFrame:
    """Fetch data for a given quarter"""
    url_template = "https://www.strokeaudit.org/Documents/National/Clinical/{}/{}-SummaryReport.aspx"
    data = requests.get(url_template.format(quarter, quarter), timeout=100).content
    try:
        df = pd.read_excel(io.BytesIO(data), sheet_name="Scoring Summary")
    except BaseException as err:
        print(f"Failed to fetch data for {quarter}: {err}")
        print(f"URL: {url_template.format(quarter, quarter)}")
        return pd.DataFrame()

    return df


def fetch_all_summary_data():
    """Fetch all data for all quarters and save to disk"""
    quarters = get_quarters()
    for quarter in quarters:
        df = fetch_summary_data(quarter)
        if df.empty:
            continue

        df = df[~df.iloc[:, 2].isna()]
        df = df.drop(columns=["Unnamed: 1", "Unnamed: 3", "Unnamed: 4"])

        # Downfill the data in the first colum where data is missing
        df.iloc[:, 0] = df.iloc[:, 0].ffill()
        df.iloc[:, 0] = df.iloc[:, 0].fillna(" ")

        # Concat the first two string columns
        df.iloc[:, 0] = df.iloc[:, 0] + " " + df.iloc[:, 1]

        # Drop the second column
        df = df.drop(df.columns[1], axis=1)

        export_path = Path("data") / "raw" / f"{quarter}.csv"
        df.to_csv(export_path, index=False)


def get_team_data(team: str):
    team_series_list = []
    quarters = []

    # Iterate through the files in the raw data folder:
    for quarter in Path("data/raw").glob("*.csv"):
        df = pd.read_csv(quarter, index_col=0)
        quarter_name = quarter.stem
        # Check if the team is in the dataframe:
        if team in df.iloc[2, :].values:
            # Get all the data for that team:
            index = df.iloc[2, :].tolist().index(team)
            team_data = df.iloc[3:, index].dropna()
            team_data.columns = [quarter_name]
            team_series_list.append(team_data)
            quarters.append(quarter_name)

    # Concatenate the dataframes:
    team_data = pd.concat(team_series_list, axis=1)

    # Convert the quarters from YEARMOMO to datetime:
    quarters = [quarter[:3] + " " + quarter[6:] for quarter in quarters]
    team_data.columns = pd.to_datetime(quarters, format="%b %Y")

    # Sort by columns
    team_data = team_data.sort_index(axis=1)

    export = Path("data") / "processed"
    export.mkdir(parents=True, exist_ok=True)

    team_data.to_csv(export / f"{team}.csv")


def get_all_scores_per_team():
    """Get all scores per team for all quarters where data exists."""

    data = []
    valid_quarters = []
    for file in Path("data/raw").glob("*.csv"):
        df = pd.read_csv(file)
        valid_quarters.append(file.stem[:3] + " " + file.stem[6:])
        scores = get_scores_per_team(df)
        data.append(scores)

    # Convert valid quarters to datetime
    valid_quarters = pd.to_datetime(valid_quarters, format="%b %Y")

    # Convert to DataFrame
    data = pd.DataFrame(data[1:], index=valid_quarters[1:])
    data.to_csv("data/data.csv")


def get_scores_per_team(df: pd.DataFrame):
    """Gets the scores per team from the DataFrame"""
    teams = df.iloc[2, 2:].values
    scores = df.iloc[4, 2:].values
    return dict(zip(teams, scores))


if __name__ == "__main__":
    fetch_all_summary_data()
    get_all_scores_per_team()
    get_team_data("Royal London Hospital HASU")