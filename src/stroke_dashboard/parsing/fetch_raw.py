from datetime import datetime
from io import BytesIO
from requests import get
from pathlib import Path

import pandas as pd

from stroke_dashboard.parsing.core import Quarter


def get_quarters():
    """Get all quarters from Q3 2013 to present day

    Note that the data is only available from Q3 2013 onwards, and some data may be
    missing for some quarters.

    Returns: list of strings for each quarter.
    """

    quarters = []
    for year in range(2013, datetime.now().year + 1):
        for quarter in Quarter:
            quarters.append(f"{quarter.value}{year}")

    return quarters


def fetch_summary_data(quarter: str) -> pd.DataFrame:
    """Fetch data for a given quarter"""
    url_template = "https://www.strokeaudit.org/Documents/National/Clinical/{}/{}-SummaryReport.aspx"
    data = get(url_template.format(quarter, quarter), timeout=100).content
    try:
        df = pd.read_excel(BytesIO(data), sheet_name="Scoring Summary")
    except BaseException as err:
        print(f"Failed to fetch data for {quarter}: {err}")
        print(f"URL: {url_template.format(quarter, quarter)}")
        raise err

    return df


def fetch_all_summary_data():
    """Fetch all data for all quarters and save to disk"""
    quarters = get_quarters()
    for quarter in quarters:
        try:
            df = fetch_summary_data(quarter)
        except BaseException as _:
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
        export_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(export_path, index=False)
