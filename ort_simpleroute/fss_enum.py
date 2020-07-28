"""
First solution strategy enum.

Relevant documentation can be found in:
https://developers.google.com/optimization/routing/routing_options
"""

from ortools.constraint_solver import routing_enums_pb2


AUTOMATIC = routing_enums_pb2.FirstSolutionStrategy.AUTOMATIC
"""
Lets the solver detect which strategy to use according to the model being solved.
"""


PATH_CHEAPEST_ARC = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
"""
Starting from a route "start" node, connect it to the node which produces the
cheapest route segment, then extend the route by iterating on the last node added
to the route.
"""


PATH_MOST_CONSTRAINED_ARC = (
    routing_enums_pb2.FirstSolutionStrategy.PATH_MOST_CONSTRAINED_ARC
)
"""
Similar to PATH_CHEAPEST_ARC, but arcs are evaluated with a comparison-based
selector which will favor the most constrained arc first. To assign a selector
to the routing model, use the method ArcIsMoreConstrainedThanArc().
"""


EVALUATOR_STRATEGY = routing_enums_pb2.FirstSolutionStrategy.EVALUATOR_STRATEGY
"""
Similar to PATH_CHEAPEST_ARC, except that arc costs are evaluated using the function
passed to SetFirstSolutionEvaluator().
"""


SAVINGS = routing_enums_pb2.FirstSolutionStrategy.SAVINGS
"""
Savings algorithm (Clarke & Wright).

Reference: Clarke, G. & Wright, J.W.:
"Scheduling of Vehicles from a Central Depot to a Number of Delivery Points",
Operations Research, Vol. 12, 1964, pp. 568-581.
"""


SWEEP = routing_enums_pb2.FirstSolutionStrategy.SWEEP
"""Sweep algorithm (Wren & Holliday).

Reference: Anthony Wren & Alan Holliday:
Computer Scheduling of Vehicles from One or More Depots to a Number of Delivery
Points Operational Research Quarterly (1970-1977),
Vol. 23, No. 3 (Sep., 1972), pp. 333-344.
"""


CHRISTOFIDES = routing_enums_pb2.FirstSolutionStrategy.CHRISTOFIDES
"""Christofides algorithm

(actually a variant of the Christofides algorithm using a maximal matching instead
of a maximum matching, which does not guarantee the 3/2 factor of the approximation
on a metric travelling salesman). Works on generic vehicle routing models by
extending a route until no nodes can be inserted on it.

Reference: Nicos Christofides, Worst-case analysis of a new heuristic for the
travelling salesman problem,
Report 388, Graduate School of Industrial Administration, CMU, 1976.
"""


ALL_UNPERFORMED = routing_enums_pb2.FirstSolutionStrategy.ALL_UNPERFORMED
"""
Make all nodes inactive. Only finds a solution if nodes are optional
(are element of a disjunction constraint with a finite penalty cost).
"""


BEST_INSERTION = routing_enums_pb2.FirstSolutionStrategy.BEST_INSERTION
"""
Iteratively build a solution by inserting the cheapest node at its cheapest
position; the cost of insertion is based on the global cost function of the routing
model. As of 2/2012, only works on models with optional nodes
(with finite penalty costs).
"""


PARALLEL_CHEAPEST_INSERTION = (
    routing_enums_pb2.FirstSolutionStrategy.PARALLEL_CHEAPEST_INSERTION
)
"""Iteratively build a solution by inserting the cheapest node at its cheapest
position; the cost of insertion is based on the arc cost function.
Is faster than BEST_INSERTION.
"""


LOCAL_CHEAPEST_INSERTION = (
    routing_enums_pb2.FirstSolutionStrategy.LOCAL_CHEAPEST_INSERTION
)
"""
Iteratively build a solution by inserting each node at its cheapest position;
the cost of insertion is based on the arc cost function.
Differs from PARALLEL_CHEAPEST_INSERTION by the node selected for insertion;
here nodes are considered in their order of creation.
Is faster than PARALLEL_CHEAPEST_INSERTION.
"""


GLOBAL_CHEAPEST_ARC = routing_enums_pb2.FirstSolutionStrategy.GLOBAL_CHEAPEST_ARC
"""Iteratively connect two nodes which produce the cheapest route segment."""


LOCAL_CHEAPEST_ARC = routing_enums_pb2.FirstSolutionStrategy.LOCAL_CHEAPEST_ARC
"""
Select the first node with an unbound successor and connect it to the node which
produces the cheapest route segment.
"""


FIRST_UNBOUND_MIN_VALUE = (
    routing_enums_pb2.FirstSolutionStrategy.FIRST_UNBOUND_MIN_VALUE
)
"""
Select the first node with an unbound successor and connect it to the first
available node.
This is equivalent to the CHOOSE_FIRST_UNBOUND strategy combined with
ASSIGN_MIN_VALUE (cf. constraint_solver.h).
"""
