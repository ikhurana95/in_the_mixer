from typing import Dict

from pydantic import BaseModel

from data_models.enums import GameWeek, PlayerName
from data_models.fpl_data import Position, PremTeam


class PredictedObjectives(BaseModel):
    expected_points: Dict[GameWeek, Dict[PlayerName, int]]
    variance_in_expected_points: Dict[GameWeek, Dict[PlayerName, int]]


class TeamStats(BaseModel):
    total_goals_conceded: int
    total_goals_scored: int
    chances_created: int
    chances_conceded: int
    xG: float
    xG_conceded: float
    posession: float


class FixtureStats(BaseModel):
    fixture: PremTeam
    home: bool
    team_stats_last_season: TeamStats
    team_stats_previous_gw: Dict[GameWeek, TeamStats]
    # form_against_team:


class ExpectationModelInputData(BaseModel):
    ict_index: float
    goals_per_90_last_season: int
    assists_per_90_last_season: int
    fraction_of_minutes_played_last_season: int
    team_form: float
    position: Position

    fixture_stats_by_gameweek: Dict[GameWeek, FixtureStats]
