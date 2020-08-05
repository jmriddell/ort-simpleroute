from ort_simpleroute._examples.original import vrp_drop_nodes as original
from ort_simpleroute import _ortools_helpers as hlp


def main():
    data = original.create_data_model()

    router = hlp.RouteOptimizer(
        len(data['distance_matrix']),
        data['num_vehicles'],
        data['depot']
    )

    router.set_global_arc_cost(lambda x, y: data['distance_matrix'][x][y])

    router.add_dimension_w_vehicle_capacity(
        lambda x: data['demands'][x],
        data['vehicle_capacities'],  # vehicle maximum capacities
        'Capacity'
    )

    penalty = 1000
    for node in range(1, len(data['distance_matrix'])):
        router.allow_drop_of_node(node, penalty)

    solution = router.solve_using_fss(hlp.fss.PATH_CHEAPEST_ARC)

    if solution:
        original.print_solution(data, router.manager, router.model, solution)


if __name__ == "__main__":
    print("\n\nOriginal\n")
    original.main()
    print("\n\nNew\n")
    main()
