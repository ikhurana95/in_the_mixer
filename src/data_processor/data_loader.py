from typing import Dict
from pandas import DataFrame
import pandas as pd
from data_models.enums import GameWeek


class GameWeekDataLoader:
    def __init__(self) -> None:
        pass

    def load_gw_dfs(self) -> Dict[GameWeek, DataFrame]: ...

    # def

    # def last_season_data(self) ->
