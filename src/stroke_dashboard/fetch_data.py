"""Module for fetching data from the SSNAP website"""

import io
from datetime import datetime
from enum import Enum
from pathlib import Path

import pandas as pd
import requests
import numpy as np


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
        df.iloc[:, 0] = (df.iloc[:, 0] + " " + df.iloc[:, 1]).str.strip()

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


def get_all_scores_per_team(level: str = "ISDN", metric: str = "SSNAP score"):
    """Get all scores per team for all quarters where data exists."""

    data = []
    valid_quarters = []
    for file in Path("data/raw").glob("*.csv"):
        df = pd.read_csv(file, index_col=0)
        try:
            scores = get_scores_per_team(df, level, metric)
        except KeyError:
            continue
        valid_quarters.append(file.stem[:3] + " " + file.stem[6:])
        data.append(scores)

    # Convert valid quarters to datetime
    valid_quarters = pd.to_datetime(valid_quarters, format="%b %Y")

    # Convert to DataFrame
    data = pd.DataFrame(data, index=valid_quarters).sort_index()

    export_folder = Path("data/overview/by_metric/")
    export_folder.mkdir(parents=True, exist_ok=True)
    export_path = export_folder / f"summary_data_{level}_{metric}.csv"
    data.to_csv(export_path)

    return data


def get_scores_per_team(
    df: pd.DataFrame, level: str = "ISDN", metric: str = "SSNAP score"
):
    """Gets the scores per team from the DataFrame"""
    # TODO: Can we find a better way of matching these?
    try:
        teams = df.loc[level].str.strip()
    except KeyError:
        # If the level is ISDN, default to SCN
        if level == "ISDN":
            teams = df.loc["SCN"].str.replace("SCN", "").str.strip()
        else:
            raise KeyError(f"Could not find level {level}")
    scores = pd.to_numeric(df.loc[metric], errors="coerce")
    return dict(zip(teams, scores))


def get_scores_broken_down_per_team():
    for team in pd.read_csv("data/data.csv", index_col=0).columns:
        get_team_data(team)


if __name__ == "__main__":
    fetch_all_summary_data()
    get_all_scores_per_team(level="ISDN")
    get_all_scores_per_team(level="Trust")
    get_all_scores_per_team(level="Team")
    get_scores_broken_down_per_team()
