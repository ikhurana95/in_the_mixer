from typing import Any, Dict
from pydantic import BaseModel

from data_models.enums import GameWeek, ORtoolsBoolVar


class SelectionStatus(BaseModel):
    in_team: ORtoolsBoolVar
    in_squad: ORtoolsBoolVar
    captain: ORtoolsBoolVar


class OptimiserVariables(BaseModel):
    selection_status: Dict[GameWeek, SelectionStatus]
    transfers: Dict[GameWeek, ORtoolsBoolVar]
