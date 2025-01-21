"""File to run all parsing functions in the correct order."""

import argparse
from stroke_dashboard.parsing.fetch_raw import fetch_all_summary_data
from stroke_dashboard.parsing.parse_data import (
    get_all_scores_per_team,
    get_scores_broken_down_per_team,
)
from stroke_dashboard.parsing.core import TeamLevel


def process_data():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--skip_fetch",
        action="store_true",
        help="Skip the fetching of data from the SSNAP website.",
    )

    args = parser.parse_args()
    if not args.skip_fetch:
        fetch_all_summary_data()

    for team_level in TeamLevel:
        get_all_scores_per_team(team_level)
        get_scores_broken_down_per_team(team_level)
        get_averages(team_level)


if __name__ == "__main__":
    process_data()
