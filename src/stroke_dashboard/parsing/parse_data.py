"""Module for fetching data from the SSNAP website"""

from pathlib import Path
import typing as tp

import pandas as pd

from stroke_dashboard.parsing.core import TeamLevel


def sanitise_names(names: tp.List[str]):
    # TODO: Also handle matching similar names together (e.g. Hospital Trust, Hospitals Trust)
    if any(["SCN" in a for a in names]):
        # Data has been encoded using SCN suffix - remove.
        return [name.replace("SCN", "").strip() for name in names]
    else:
        # No SCN in the column names - can continue
        return names


def get_team_data(team: str, mode: TeamLevel = TeamLevel.TEAM):
    team_series_list = []
    quarters = []

    # Iterate through the files in the raw data folder:
    for quarter in Path("data/raw").glob("*.csv"):
        df = pd.read_csv(quarter, index_col=0, header=None)

        names = df.iloc[mode.value, :].values.tolist()
        if mode == TeamLevel.ISDN:
            names = sanitise_names(names)

        quarter_name = quarter.stem

        # Check if the team is in the dataframe:
        if team in names:
            # Get all the data for that team:
            index = names.index(team)
            team_data = df.iloc[3:, index].dropna()
            team_data.columns = [quarter_name]
            team_series_list.append(team_data)
            quarters.append(quarter_name)

    # Concatenate the dataframes:
    try:
        team_data = pd.concat(team_series_list, axis=1)
    except ValueError:
        print(f"Could not concatenate dataframes for {team}")
        return

    # Convert the quarters from YEARMOMO to datetime:
    quarters = [quarter[:3] + " " + quarter[6:] for quarter in quarters]
    team_data.columns = pd.to_datetime(quarters, format="%b %Y")

    # Sort by columns
    team_data = team_data.sort_index(axis=1)

    export = Path("data") / "processed" / mode.name
    export.mkdir(parents=True, exist_ok=True)

    team_data.to_csv(export / f"{team}.csv")


def get_all_scores_per_team(
    level: TeamLevel = TeamLevel.ISDN,
    metric: str = "SSNAP score",
):
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
    data_df = pd.DataFrame(data, index=valid_quarters).sort_index()

    export_folder = Path("data/overview/by_metric/")
    export_folder.mkdir(parents=True, exist_ok=True)
    export_path = export_folder / f"summary_data_{level.to_col_name()}_{metric}.csv"
    data_df.to_csv(export_path)

    return data


def get_scores_per_team(
    df: pd.DataFrame, level: TeamLevel = TeamLevel.ISDN, metric: str = "SSNAP score"
):
    """Gets the scores per team from the DataFrame"""
    teams = sanitise_names(df.loc[level.to_col_name()].tolist())
    scores = pd.to_numeric(df.loc[metric], errors="coerce")
    if isinstance(scores, pd.DataFrame):
        scores = scores.tolist()
    return dict(zip(teams, scores))


def get_scores_broken_down_per_team(mode: TeamLevel):
    df = (
        Path("data")
        / "overview"
        / "by_metric"
        / f"summary_data_{mode.to_col_name()}_SSNAP score.csv"
    )

    df = pd.read_csv(df, index_col=0)

    for agg in df.columns:
        get_team_data(agg, mode)
