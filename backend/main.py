from OSRM import (
    get_driver,
    get_passenger,
    get_route,
    get_carpool_route
)
from fuzzy_logic import calculate_compatibility, evaluate_rules, fuzzify, D_range, T_range, Percent_range, C_range, D_sets, T_sets, Percent_sets, C_sets, rules
from route_compatibility import calculate_route_compatibility
from map import visualize_route


def main():

    # 1. Retrieve driver and passenger information
    driver = get_driver("D1")
    passenger = get_passenger("P2")

    # 2. Calculate original driver route
    original_route = get_route(
        driver["startPoint"],
        driver["Destination"]
    )

    # 3. Calculate alternative carpool route
    carpool_route = get_carpool_route(
        driver,
        passenger
    )

    # 4. Visualize both routes
    visualize_route(
        driver,
        passenger,
        original_route,
        carpool_route
    )

    # 5. Calculate route compatibility
    result = calculate_route_compatibility(
        driver,
        passenger
    )

    score = calculate_compatibility(
        result['detour_distance'],
        result['detour_time'],
        result['detour_percentage']
    )

    # 6. Display results
    print("\n--- ROUTE COMPARISON ---")

    print(
        f"Original Distance: "
        f"{original_route['distance_km']:.2f} km"
    )

    print(
        f"Carpool Distance: "
        f"{carpool_route['distance_km']:.2f} km"
    )

    print(
        f"Additional Distance: "
        f"{result['detour_distance']:.2f} km"
    )

    print(
        f"\nOriginal Time: "
        f"{original_route['duration_min']:.2f} minutes"
    )

    print(
        f"Carpool Time: "
        f"{carpool_route['duration_min']:.2f} minutes"
    )

    print(
        f"Additional Time: "
        f"{result['detour_time']:.2f} minutes"
    )

    print(
        f"Detour Percentage: "
        f"{result['detour_percentage']:.2f}%"
    )

    print(
        f"Compatibility Score: "
        f"{score:.2f}/100"
    )

    test_cases = [
        {
        "name": "Good Distance, Bad Time",
        "distance": 1,
        "time": 14,
        "percentage": 30
    },
    {
        "name": "Bad Distance, Good Time",
        "distance": 4.5,
        "time": 3,
        "percentage": 350
    },
    {
        "name": "Boundary Time",
        "distance": 2,
        "time": 15,
        "percentage": 80
    }
    ]

    print("\n--- FUZZY LOGIC TESTING ---")

    for case in test_cases:

        score = calculate_compatibility(
            case["distance"],
            case["time"],
            case["percentage"]
        )
       

        print(f"\nScenario: {case['name']}")
        print(f"Distance: {case['distance']} km")
        print(f"Additional Time: {case['time']} minutes")
        print(f"Detour Percentage: {case['percentage']}%")
        print(f"Compatibility Score: {score:.2f}/100")



if __name__ == "__main__":
    main()