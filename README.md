# ORT Simpleroute

A wrapper around Google's python library [ORTools](https://github.com/google/or-tools) routing solver.

## Reason

`ortools` routing solver exposes internal mechanics regarding node and callback management.

The goal of this package is to make a simpler interface, but focusing on keeping all the flexibility and functionality possible from the original library.

## Differences from ORTools

For more details look into the examples folder, there are original examples from the ortools repositoty and reimplementations.

### Routing Model and Index Manager

#### ortools
ORTools has a `RoutingModel` class that takes all parameters for performing an optimization, however, when a node has to be referenced, it has to be done providing an internal index assigned to each node, that's why a Index Manager is needed to transform between internal and actual node number for a given node.

```python
# Initializing a index manager and a routing model
index_manager = pywrapcp.RoutingIndexManager(ammount_of_nodes, num_vehicles, depot)
routing_model = pywrapcp.RoutingModel(index_manager)

# A callback for providing distances have to be in terms of internal indexes
def index_distance_callback(from_index, to_index):
    from_node = manager.IndexToNode(from_index)
    to_node = manager.IndexToNode(to_index)
    return distance_matrix[from_node][to_node]
```

#### ort_simpleroute

`RoutingModel` and `RoutingIndexManager` are contained inside `RouteOptimizer` which handles all the conversion internally.

```python
# Initializing the route optimizer
router = ort_simpleroute.RouteOptimizer(ammount_of_nodes, num_vehicles, depot)

# A distance callback, no index conversion required
def distance_callback(from_node, to_node):
    return distance_matrix[from_node][to_node]
```
### Callback management

#### ortools

To use a callback for retrieving values to the solver, the callback has to be registered, in the registration process a index is assigned to that callback, only then the callback can be assigned to a task in the solver, using its index.

```python
distance_callback_index = routing.RegisterTransitCallback(index_distance_callback)
routing_model.SetArcCostEvaluatorOfAllVehicles(distance_callback_index)
```

#### ort_simpleroute

Callback are provided directly.

```python
router.set_global_arc_cost(distance_callback)
```
## Testing against original ortools examples

To test the proper funcioning of the wrapper, untouched [original example files from the ortools repository](https://github.com/google/or-tools/tree/stable/ortools/constraint_solver/samples) are used to compare against reimplementations using this package. The tests and example files are under the `test_examples_same_output` subpackage.

The reason for using the original files untouched is to avoid the need to specify changes made to those files as required by the Apache license, and also to make testing against more files simpler.
