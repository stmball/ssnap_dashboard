"""Core classes and enums for parsing the raw data"""

from enum import Enum


class Quarter(Enum):
    """Enum for the quarters of the year"""

    Q1 = "JanMar"
    Q2 = "AprJun"
    Q3 = "JulSep"
    Q4 = "OctDec"


class TeamLevel(Enum):
    """Enum for the different levels of data"""

    ISDN = 1
    TRUST = 2
    TEAM = 3

    def to_col_name(self):
        """Convert the enum to a column name in the raw data"""
        match self:
            case TeamLevel.ISDN:
                return "ISDN"
            case TeamLevel.TRUST:
                return "Trust"
            case TeamLevel.TEAM:
                return "Team"
