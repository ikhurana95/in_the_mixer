from typing import Dict
from ortools.linear_solver import pywraplp

from data_models.enums import PlayerName
from data_models.fpl_data import FPLData, Position, PremTeam
from data_models.optimiser_variables import SelectionStatus


class FPLBaseOptimiser:
    def __init__(self, fpl_data: FPLData) -> None:

        self.fpl_data = fpl_data

        self._solver = None
        self._objective = None
        self._team_selection_vars = None

    @property
    def solver(self):
        if self._solver is None:
            self._solver = pywraplp.Solver.CreateSolver("SCIP")
        return self._solver

    @property
    def objective(self):
        if self._objective is None:
            self._objective = self.solver.Objective()
        return self._objective

    @property
    def team_selection_vars(self) -> Dict[PlayerName, SelectionStatus]:
        if self._team_selection_vars is None:
            self._team_selection_vars = {
                player_name: SelectionStatus(
                    in_squad=self.solver.BoolVar(f"{player_name}_in_squad"),
                    in_team=self.solver.BoolVar(f"{player_name}_in_team"),
                    captain=self.solver.BoolVar(f"{player_name}_captain"),
                )
                for player_name in self.fpl_data
            }
        return self._team_selection_vars

    def fpl_team_constraints(self): ...

    def squad_size_constraint(self):
        self.solver.Add(
            sum(
                selection_status.in_squad
                for _, selection_status in self.team_selection_vars.items()
            )
            == 15
        )

    def squad_cost_constraint(self):
        self.solver.Add(
            sum(
                selection_status.in_squad * self.fpl_data.players[player_name].cost
                for player_name, selection_status in self.team_selection_vars.items()
            )
            == 1000
        )

    ## No more than 3 players from 1 team constraint
    def max_players_from_single_team_in_squad_constraint(self):
        for prem_team in PremTeam:
            self.solver.Add(
                sum(
                    selection_status.in_squad
                    * int(self.fpl_data.players[player_name].team == prem_team)
                    for player_name, selection_status in self.team_selection_vars.items()
                )
                <= 3
            )

    ## Position Constraint
    def squad_positional_constraints(self):

        self.solver.Add(
            sum(
                selection_status.in_squad
                * int(
                    self.fpl_data.players[player_name].position == Position.goalkeeper
                )
                for player_name, selection_status in self.team_selection_vars.items()
            )
            == 2
        )

        self.solver.Add(
            sum(
                selection_status.in_squad
                * int(self.fpl_data.players[player_name].position == Position.defender)
                for player_name, selection_status in self.team_selection_vars.items()
            )
            == 5
        )

        self.solver.Add(
            sum(
                selection_status.in_squad
                * int(
                    self.fpl_data.players[player_name].position == Position.midfielder
                )
                for player_name, selection_status in self.team_selection_vars.items()
            )
            == 5
        )
        self.solver.Add(
            sum(
                selection_status.in_squad
                * int(self.fpl_data.players[player_name].position == Position.forward)
                for player_name, selection_status in self.team_selection_vars.items()
            )
            == 3
        )

    def squad_positional_constraints(self):

        self.solver.Add(
            sum(
                selection_status.in_team
                * int(
                    self.fpl_data.players[player_name].position == Position.goalkeeper
                )
                for player_name, selection_status in self.team_selection_vars.items()
            )
            == 1
        )

        self.solver.Add(
            sum(
                selection_status.in_team
                * int(self.fpl_data.players[player_name].position == Position.defender)
                for player_name, selection_status in self.team_selection_vars.items()
            )
            >= 3
        )

        self.solver.Add(
            sum(
                selection_status.in_team
                * int(self.fpl_data.players[player_name].position == Position.forward)
                for player_name, selection_status in self.team_selection_vars.items()
            )
            >= 1
        )

    def team_size_constraint(self):
        sum(
            selection_status.in_team
            for _, selection_status in self.team_selection_vars.items()
        ) == 11
