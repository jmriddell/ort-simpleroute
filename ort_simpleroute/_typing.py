"""
Typing specific for this package.

To copy and paste:
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
    Route,
)
"""

from typing import Callable, Union, Sequence
from ortools.constraint_solver import pywrapcp


Manager = pywrapcp.RoutingIndexManager
Model = pywrapcp.RoutingModel
Solution = Model.SolveWithParameters

_Magnitude = Union[float, int]
Distance = _Magnitude
Demand = _Magnitude

Node = int
Index = int

NDistanceCallback = Callable[[Node, Node], Distance]
IDistanceCallback = Callable[[Index, Index], Distance]

SearchParameters = pywrapcp.DefaultRoutingSearchParameters

Route = Sequence[Node]
