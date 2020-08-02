from . import capacity_constraint as original
from .. import _ortools_helpers as hlp


def main():
    data = original.create_data_model()

    router = hlp.ConvenientModel(
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

    solution = router.solve_using_fss(hlp.fss.PATH_CHEAPEST_ARC)

    if solution:
        original.print_solution(data, router.manager, router.model, solution)


if __name__ == "__main__":
    print("\n\nOriginal\n")
    original.main()
    print("\n\nNew\n")
    main()