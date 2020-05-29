"""Handy classes and functions to access to ortools routing functionalities."""
from typing import Generator
from ortools.constraint_solver import pywrapcp, routing_enums_pb2
from ._typing import (
    Manager,
    Model,
    Solution,
    Distance,
    Node,
    Index,
    NDistanceCallback,
    IDistanceCallback,
    SearchParameters,
)


def make_search_parameters() -> SearchParameters:
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.GLOBAL_CHEAPEST_ARC
    )
    return search_parameters


def node2index_distance_callback(
    manager: Manager, node_distance_callback: NDistanceCallback
) -> IDistanceCallback:
    def index_distance_callback(from_index: Index, to_index: Index) -> Distance:
        """Returns the distance between the two nodes."""
        # Convert from routing variable Index to distance matrix NodeIndex.
        from_node: Node = manager.IndexToNode(from_index)
        to_node: Node = manager.IndexToNode(to_index)
        return node_distance_callback(from_node, to_node)

    return index_distance_callback


class ConvenientModel:
    """Class to group the routing manager and model, and functions with side effects."""

    def __init__(self, num_nodes: int, num_vehicles: int = 1, depot: int = 0):
        self.manager: Manager = pywrapcp.RoutingIndexManager(
            num_nodes, num_vehicles, depot
        )
        self.model: Model = pywrapcp.RoutingModel(self.manager)

    def set_global_arc_cost(self, distance_callback):
        index_distance_callback = node2index_distance_callback(
            self.manager, distance_callback
        )
        transit_callback_index = self.model.RegisterTransitCallback(
            index_distance_callback
        )
        self.model.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)


def solution_sequence(
    rmod: ConvenientModel, solution: Solution
) -> Generator[Node, None, None]:
    index = rmod.model.Start(0)
    while not rmod.model.IsEnd(index):
        yield rmod.manager.IndexToNode(index)
        index = solution.Value(rmod.model.NextVar(index))
    yield rmod.manager.IndexToNode(index)
