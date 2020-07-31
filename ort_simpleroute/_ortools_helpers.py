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
from enum import Enum


# Search Parameters
# ----- start

# GLOBAL_CHEAPEST_ARC
# PATH_CHEAPEST_ARC
def make_search_parameters(fss_enum) -> SearchParameters:
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = fss_enum
    return search_parameters


# ----- end


def node2index_distance_callback(
    manager: Manager, node_distance_callback: NDistanceCallback
) -> IDistanceCallback:
    def index_distance_callback(from_index: Index, to_index: Index) -> Distance:
        """Return the distance between the two nodes."""
        # Convert from routing variable Index to distance matrix NodeIndex.
        from_node: Node = manager.IndexToNode(from_index)
        to_node: Node = manager.IndexToNode(to_index)
        return node_distance_callback(from_node, to_node)

    return index_distance_callback


def node2index_demand_callback(
    manager: Manager, node_demand_callback: NDistanceCallback
):
    def index_demand_callback(from_index):
        """Return the demand of the node."""
        # Convert from routing variable Index to demands NodeIndex.
        from_node = manager.IndexToNode(from_index)
        return node_demand_callback(from_node)

    return index_demand_callback


def _is_callback(callback_or_index):
    """Return True if object is callable, false if int, else raise exception."""
    if callable(callback_or_index):
        return True
    elif isinstance(callback_or_index, int):
        return False
    raise TypeError("A callback should be callable or represented by a index.")


def _argument_count(callback):
    from inspect import signature

    sig = signature(callback)
    return len(sig.parameters)


class _CallbackIndexTracker:
    def __init__(self):
        self._callbacks_and_indexes = dict()

    def add_callback(self, callback, callback_index):
        if not callable(callback):
            raise TypeError("callback argument must be callable.")
        if not isinstance(callback_index, int):
            raise TypeError("callback_index argument must be int.")

        self._callbacks_and_indexes[callback] = callback_index
        self._callbacks_and_indexes[callback_index] = callback

    def _get(self, callback_or_index, get_callback=True, die_if_not_present=False):
        assert isinstance(get_callback, bool)
        assert isinstance(die_if_not_present, bool)

        if die_if_not_present:
            getted = self._callbacks_and_indexes[callback_or_index]
        else:
            getted = self._callbacks_and_indexes.get(callback_or_index)
            if getted is None:
                return

        if _is_callback(getted) == get_callback:
            return getted
        return self._callbacks_and_indexes[getted]

    def get_callback(self, callback_or_index):
        return self._get(callback_or_index, get_callback=True)

    def get_index(self, callback_or_index):
        index = self._get(callback_or_index, get_callback=False)
        assert isinstance(index, int) or index is None
        return index

    def is_present(self, callback_or_index):
        return callback_or_index in self._callbacks_and_indexes


class CallbackTypes(Enum):
    ANY = 0
    UNARY = 1
    TRANSIT = 2


def _check_callback(callback, callback_type=CallbackTypes.ANY):
    """Raise exception if invalid callback, return True if matches type else False."""
    if not _is_callback(callback):
        raise TypeError("callback argument not callable.")
    if callback_type not in CallbackTypes:
        raise ValueError("Wrong callback_type provided.")

    arg_count = _argument_count(callback)
    is_unary = arg_count == 1
    is_transit = arg_count == 2

    if not (is_transit or is_unary):
        raise ValueError("Wrong callback ammount of arguments.")
    if callback_type is CallbackTypes.ANY:
        return True
    if is_unary and callback_type is CallbackTypes.UNARY:
        return True
    if is_transit and callback_type is CallbackTypes.TRANSIT:
        return True
    return False


class _CallbackManager:
    def __init__(self, model, manager):
        self.manager = manager
        self.model = model
        self._callback_index_tracker = _CallbackIndexTracker()

    def _register_transit_callback(self, distance_callback: NDistanceCallback) -> int:
        """
        Register a callback, assign an internal index to it, and return its index.

        The internal index is returned in order to later tell the model how to use the
        callback, which now will be referenced by it's index. That way it will be
        possible to use the same callback function for multiple purposes like for more
        than one vehicle but not all.
        """
        index_distance_callback: IDistanceCallback = node2index_distance_callback(
            self.manager, distance_callback
        )
        transit_callback_index = self.model.RegisterTransitCallback(
            index_distance_callback
        )
        return transit_callback_index

    def _register_unary_callback(self, demand_callback):
        """
        Register a callback, assign an internal index to it, and return its index.

        Same as register_transit_callback but the callback thakes just one argument
        and returns a value associated to a node instead of a path.
        """
        index_distance_callback = node2index_demand_callback(
            self.manager, demand_callback
        )
        unary_callback_index = self.model.RegisterUnaryTransitCallback(
            index_distance_callback
        )
        return unary_callback_index

    def _register_callback(self, callback):
        if self._callback_index_tracker.is_present(callback):
            raise ValueError("Callback already present.")
        argument_count = _argument_count(callback)
        if argument_count == 1:
            callback_index = self._register_unary_callback(callback)
        elif argument_count == 2:
            callback_index = self._register_transit_callback(callback)
        else:
            raise ValueError("Callback needs to have 1 or 2 arguments.")
        self._callback_index_tracker.add_callback(callback, callback_index)

    def callback_to_index(self, callback, require_type=CallbackTypes.ANY):
        """Get index of callback and register if not already present."""
        if not _check_callback(callback, callback_type=require_type):
            raise ValueError("Required callback type doesn't match")
        index = self._callback_index_tracker.get_index(callback)
        if index is None:
            self._register_callback(callback)
            index = self._callback_index_tracker.get_index(callback)
            assert index is not None
        return index


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

        self._callback_manager = _CallbackManager(self.model, self.manager)

        self._deliveries_enabled = False

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
