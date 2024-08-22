from typing import Dict
from ortools.linear_solver import pywraplp

from data_models.enums import GameWeek, PlayerName
from data_models.expectation_models import PredictedObjectives
from data_models.fpl_data import FPLData, FplTeam, Position, PremTeam
from data_models.optimiser_variables import SelectionStatus


class FPLBaseOptimiser:
    def __init__(self, fpl_data: FPLData, number_of_gameweeks: int) -> None:

        self.fpl_data = fpl_data
        self.num_game_weeks = number_of_gameweeks
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
    def team_selection_vars(self) -> Dict[GameWeek, Dict[PlayerName, SelectionStatus]]:
        if self._team_selection_vars is None:
            self._team_selection_vars = {
                game_week: {
                    player_name: SelectionStatus(
                        in_squad=self.solver.BoolVar(f"{player_name}_in_squad"),
                        in_team=self.solver.BoolVar(f"{player_name}_in_team"),
                        captain=self.solver.BoolVar(f"{player_name}_captain"),
                    )
                    for player_name in self.fpl_data.players
                }
                for game_week in range(1, self.num_game_weeks, 1)
            }
        return self._team_selection_vars

    def squad_size_constraint(self):
        for game_week, game_week_team_selection in self.team_selection_vars.items():
            self.solver.Add(
                sum(
                    selection_status.in_squad
                    for _, selection_status in game_week_team_selection.items()
                )
                == 15
            )

    def squad_cost_constraint(self):
        for game_week, game_week_team_selection in self.team_selection_vars.items():
            self.solver.Add(
                sum(
                    selection_status.in_squad * self.fpl_data.players[player_name].cost
                    for player_name, selection_status in game_week_team_selection.items()
                )
                == 1000
            )

    ## No more than 3 players from 1 team constraint
    def max_players_from_single_team_in_squad_constraint(self):
        for game_week, game_week_team_selection in self.team_selection_vars.items():
            for prem_team in PremTeam:
                self.solver.Add(
                    sum(
                        selection_status.in_squad
                        * int(self.fpl_data.players[player_name].team == prem_team)
                        for player_name, selection_status in game_week_team_selection.items()
                    )
                    <= 3
                )

    ## Position Constraint
    def squad_positional_constraints(self):
        for game_week, game_week_team_selection in self.team_selection_vars.items():

            self.solver.Add(
                sum(
                    selection_status.in_squad
                    * int(
                        self.fpl_data.players[player_name].position
                        == Position.goalkeeper
                    )
                    for player_name, selection_status in game_week_team_selection.items()
                )
                == 2
            )

            self.solver.Add(
                sum(
                    selection_status.in_squad
                    * int(
                        self.fpl_data.players[player_name].position == Position.defender
                    )
                    for player_name, selection_status in game_week_team_selection.items()
                )
                == 5
            )

            self.solver.Add(
                sum(
                    selection_status.in_squad
                    * int(
                        self.fpl_data.players[player_name].position
                        == Position.midfielder
                    )
                    for player_name, selection_status in game_week_team_selection.items()
                )
                == 5
            )
            self.solver.Add(
                sum(
                    selection_status.in_squad
                    * int(
                        self.fpl_data.players[player_name].position == Position.forward
                    )
                    for player_name, selection_status in game_week_team_selection.items()
                )
                == 3
            )

    def team_positional_constraints(self):
        for game_week, game_week_team_selection in self.team_selection_vars.items():

            self.solver.Add(
                sum(
                    selection_status.in_team
                    * int(
                        self.fpl_data.players[player_name].position
                        == Position.goalkeeper
                    )
                    for player_name, selection_status in game_week_team_selection.items()
                )
                == 1
            )

            self.solver.Add(
                sum(
                    selection_status.in_team
                    * int(
                        self.fpl_data.players[player_name].position == Position.defender
                    )
                    for player_name, selection_status in game_week_team_selection.items()
                )
                >= 3
            )

            self.solver.Add(
                sum(
                    selection_status.in_team
                    * int(
                        self.fpl_data.players[player_name].position == Position.forward
                    )
                    for player_name, selection_status in game_week_team_selection.items()
                )
                >= 1
            )

    def team_size_constraint(self):
        for game_week, game_week_team_selection in self.team_selection_vars.items():

            self.solver.Add(
                sum(
                    selection_status.in_team
                    for _, selection_status in game_week_team_selection.items()
                )
                == 11
            )

    def single_captain_constraint(self):
        for game_week, game_week_team_selection in self.team_selection_vars.items():

            self.solver.Add(
                sum(
                    selection_status.captain
                    for _, selection_status in game_week_team_selection.items()
                )
                == 1
            )

    def players_in_team_must_be_in_squad(self):
        for game_week, game_week_team_selection in self.team_selection_vars.items():
            for player_name, selection_status in game_week_team_selection.items():
                self.solver.Add(selection_status.in_squad >= selection_status.in_team)

    def captain_must_be_in_team(self):
        for game_week, game_week_team_selection in self.team_selection_vars.items():
            for player_name, selection_status in game_week_team_selection.items():
                self.solver.Add(selection_status.in_team >= selection_status.captain)

    def fpl_team_constraints(self):
        self.squad_size_constraint()
        self.squad_cost_constraint()
        self.squad_positional_constraints()
        self.max_players_from_single_team_in_squad_constraint()

        self.team_size_constraint()
        self.team_positional_constraints()
        self.players_in_team_must_be_in_squad()
        self.captain_must_be_in_team()

    def setup_solver_with_team_constraints(self):
        self.fpl_team_constraints()


class InitialSquadOptimiser(FPLBaseOptimiser):
    def __init__(self, fpl_data: FPLData) -> None:
        super().__init__(fpl_data, number_of_gameweeks=1)

    def print_results(self, status): ...

    def add_objective(self): ...

    def optimise(self):
        self.setup_solver_with_team_constraints()
        self.add_objective()
        status = self.solver.solve()
        self.print_results(status)


class GameWeekOptimisation(FPLBaseOptimiser):
    def __init__(
        self,
        fpl_data: FPLData,
        current_team: FplTeam,
        number_of_gameweeks: int,
        predicted_objectives: PredictedObjectives,
    ) -> None:
        super().__init__(fpl_data, number_of_gameweeks=number_of_gameweeks)
        self.current_team = current_team
        self.predicted_objectives = predicted_objectives

    def transfer_limit_constraint(self):
        for game_week, game_week_team_selection in self.team_selection_vars.items():
            if game_week == 1:
                self.solver.Add(
                    sum(
                        (
                            (player_name in self.current_team.players)
                            != new_squad_selection_status.in_squad
                        )
                        for player_name, new_squad_selection_status in game_week_team_selection.items()
                    )
                    <= 1
                )
            else:
                self.solver.Add(
                    sum(
                        (
                            self.team_selection_vars[game_week - 1][player_name]
                            != new_squad_selection_status.in_squad
                        )
                        for player_name, new_squad_selection_status in game_week_team_selection.items()
                    )
                    <= 1
                )

    def print_results(self, status): ...

    def add_objective(self):
        for game_week, game_week_team_selection in self.team_selection_vars.items():
            for player_name, selection_status in game_week_team_selection.items():

                self.objective.SetCoefficient(
                    selection_status.in_team,
                    self.predicted_objectives.expected_points[game_week][player_name],
                )
        self.objective.SetMaximization()

    def optimise(self):
        self.setup_solver_with_team_constraints()
        self.transfer_limit_constraint()
        self.add_objective()
        status = self.solver.solve()
        self.print_results(status)
