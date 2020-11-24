from ort_simpleroute.test_examples_same_output._examples.original import (
    vrp_pickup_delivery as original,
)
from ort_simpleroute import _ortools_helpers as hlp


def main():
    """Entry point of the program."""
    # Instantiate the data problem.
    data = original.create_data_model()

    # Create the router.
    router = hlp.RouteOptimizer(
        len(data["distance_matrix"]), data["num_vehicles"], data["depot"]
    )

    # Define cost of each arc.
    def distance_callback(from_node, to_node):
        """Returns the manhattan distance between the two nodes."""
        return data["distance_matrix"][from_node][to_node]

    router.set_global_arc_cost(distance_callback)

    # Add Distance constraint.
    # dimension_name = 'Distance'
    distance_dimension = router.add_dimension(
        distance_callback,
        3000,  # vehicle maximum travel distance
        "Distance",  # Dimension Name
    )
    distance_dimension.SetGlobalSpanCostCoefficient(100)

    # Define Transportation Requests.
    for request in data["pickups_deliveries"]:
        router.add_delivery_request(request[0], request[1])

    # Solve the problem using PARALLEL_CHEAPEST_INSERTION first solution heuristic.
    solution = router.solve_using_fss(hlp.fss.PARALLEL_CHEAPEST_INSERTION)

    if solution:
        original.print_solution(data, router.manager, router.model, solution)


if __name__ == "__main__":
    print("\n\nOriginal\n")
    original.main()
    print("\n\nNew\n")
    main()
