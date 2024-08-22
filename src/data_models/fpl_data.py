from enum import StrEnum
from typing import Dict, List
from pydantic import BaseModel

from data_models.enums import GameWeek, PlayerName


class Position(StrEnum):
    goalkeeper = "GK"  # Goalkeeper
    defender = "DEF"  # Defender
    midfielder = "MID"  # Midfielder
    forward = "FWD"  # Forward


class PremTeam(StrEnum):
    BOURNEMOUTH = "Bournemouth"
    NOTTM_FOREST = "Nott'm Forest"
    ARSENAL = "Arsenal"
    CRYSTAL_PALACE = "Crystal Palace"
    SOUTHAMPTON = "Southampton"
    ASTON_VILLA = "Aston Villa"
    SPURS = "Spurs"
    WOLVES = "Wolves"
    BRENTFORD = "Brentford"
    CHELSEA = "Chelsea"
    BRIGHTON = "Brighton"
    LEICESTER = "Leicester"
    IPSWICH = "Ipswich"
    MAN_UTD = "Man Utd"
    WEST_HAM = "West Ham"
    FULHAM = "Fulham"
    LIVERPOOL = "Liverpool"
    NEWCASTLE = "Newcastle"
    MAN_CITY = "Man City"
    EVERTON = "Everton"


class PlayerStats(BaseModel):
    ict_index: float
    total_points_last_season: int
    minutes_played_last_season: float


# Example usage
class FantasyPlayer(BaseModel):
    name: str
    team: PremTeam
    position: Position
    stats: PlayerStats
    cost: int


class Fixtures(BaseModel):
    home_games: Dict[PremTeam, PremTeam]
    away_games: Dict[PremTeam, PremTeam]


class FPLData(BaseModel):
    players: Dict[PlayerName, FantasyPlayer]
    fixtures: Dict[GameWeek, Fixtures]


class FplTeam(BaseModel):
    players: Dict[PlayerName, FantasyPlayer]
