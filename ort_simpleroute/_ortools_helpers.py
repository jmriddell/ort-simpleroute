"""Handy classes and functions to access ortools routing functionalities."""
from sys import maxsize
from typing import Generator, List
from ortools.constraint_solver import pywrapcp, routing_enums_pb2
from ._typing import (
    Manager,
    Model,
    Solution,
    Distance,
    Demand,
    Node,
    Index,
    NDistanceCallback,
    IDistanceCallback,
    SearchParameters,
)
from . import fss_enum as fss
from ._callback_management import CallbackManager, CallbackTypes


def make_search_parameters(fss_enum) -> SearchParameters:
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = fss_enum
    return search_parameters


_add_dimension_error = RuntimeError(
    "Failed to add dimension, " + "is possible that the name provided is already used."
)


class ConvenientModel:
    """Class to group the routing manager and model, and functions with side effects."""

    def __init__(self, num_nodes: int, num_vehicles: int = 1, depot: int = 0):
        self.manager: Manager = pywrapcp.RoutingIndexManager(
            num_nodes, num_vehicles, depot
        )
        self.model: Model = pywrapcp.RoutingModel(self.manager)

        self._callback_manager = CallbackManager(self.model, self.manager)

        self._deliveries_enabled = False
        self._cumul_dim = None  # Defined to a dimension when deliveries enabled

    def set_global_arc_cost(self, distance_callback):
        transit_callback_index = self._callback_manager.callback_to_index(
            distance_callback,
            require_type=CallbackTypes.TRANSIT
        )
        self.model.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    def set_vehicle_arc_cost(self, distance_callback, vehicle_num: int):
        transit_callback_index = self._callback_manager.callback_to_index(
            distance_callback,
            require_type=CallbackTypes.TRANSIT
        )
        self.model.SetArcCostEvaluatorOfVehicle(transit_callback_index, vehicle_num)

    def add_dimension(
        self,
        callback,
        capacity: int,
        name: str,
        slack_max=0,
        fix_start_cumul_to_zero: bool = True,
    ):
        """https://developers.google.com/optimization/reference/python/constraint_solver/pywrapcp#adddimension"""
        callback_index = self._callback_manager.callback_to_index(callback)
        success = self.model.AddDimension(
            callback_index,
            slack_max,  # capacity slack
            capacity,  # max capacity of all vehicles
            fix_start_cumul_to_zero,  # start cumul to zero
            name,
        )
        if success:
            return self.model.GetDimensionOrDie(name)
        raise _add_dimension_error

    def add_dimension_w_vehicle_capacity(
        self,
        callback,
        vehicle_capacities: List[Demand],
        name: str,
        slack_max=0,
        fix_start_cumul_to_zero: bool = True,
    ):
        callback_index = self._callback_manager.callback_to_index(callback)
        success = self.model.AddDimensionWithVehicleCapacity(
            callback_index,
            slack_max,  # capacity slack
            vehicle_capacities,  # vehicle maximum capacities
            fix_start_cumul_to_zero,  # start cumul to zero
            name,
        )
        if success:
            return self.model.GetDimensionOrDie(name)
        raise _add_dimension_error

    def solve_using_fss(self, fss_enum):
        search_parameters = make_search_parameters(fss_enum)
        return self.model.SolveWithParameters(search_parameters)

    def optimize_solution(self, initial_solution, time_limit=None, solution_limit=None):
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        if time_limit is not None:
            search_parameters.time_limit.seconds = time_limit
        if solution_limit is not None:
            search_parameters.solution_limit = solution_limit

        return self.model.SolveFromAssignmentWithParameters(
            initial_solution, search_parameters
        )

    def _enable_deliveries(self):
        if self._deliveries_enabled:
            return
        self._cumul_dim = self.add_dimension(lambda x, y: 1, maxsize, "_cumul")
        self._deliveries_enabled = True

    def add_delivery_request(self, from_node, to_node):
        self._enable_deliveries()
        pickup_index = self.manager.NodeToIndex(from_node)
        delivery_index = self.manager.NodeToIndex(to_node)
        self.model.AddPickupAndDelivery(pickup_index, delivery_index)
        self.model.solver().Add(
            self.model.VehicleVar(pickup_index) == self.model.VehicleVar(delivery_index)
        )
        self.model.solver().Add(
            self._cumul_dim.CumulVar(pickup_index)
            <= self._cumul_dim.CumulVar(delivery_index)
        )

    def allow_drop_of_node(self, node, penalty):
        self.model.AddDisjunction([self.manager.NodeToIndex(node)], penalty)


def solution_sequence(
    rmod: ConvenientModel, solution: Solution
) -> Generator[Node, None, None]:
    index = rmod.model.Start(0)
    while not rmod.model.IsEnd(index):
        yield rmod.manager.IndexToNode(index)
        index = solution.Value(rmod.model.NextVar(index))
    yield rmod.manager.IndexToNode(index)
