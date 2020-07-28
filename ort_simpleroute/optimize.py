from . import _ortools_helpers as hlp

from typing import Sequence, Callable, Union, Generator
from ._typing import Node, NDistanceCallback, Solution, Route, Union


def optimize_route(
    distance_callback: NDistanceCallback,
    num_nodes: int,
    num_vehicles: int = 1,
    depot: Node = 0,
) -> Union[Route, None]:
    rmod = hlp.ConvenientModel(num_nodes, num_vehicles, depot)

    rmod.set_global_arc_cost(distance_callback)

    search_parameters = hlp.make_search_parameters('GLOBAL_CHEAPEST_ARC')

    solution: Solution = rmod.model.SolveWithParameters(search_parameters)

    if solution:
        return list(hlp.solution_sequence(rmod, solution))
    return None


def optimize_matrix(
    matrix, num_vehicles: int = 1, depot: Node = 0
) -> Union[Route, None]:
    def node_distance_callback(from_node, to_node):
        return matrix[from_node, to_node]

    return optimize_route(
        node_distance_callback, len(matrix), num_vehicles=num_vehicles, depot=depot
    )
