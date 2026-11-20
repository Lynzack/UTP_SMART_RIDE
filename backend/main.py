from OSRM import (
    get_driver,
    get_passenger,
    get_route,
    get_carpool_route
)

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


if __name__ == "__main__":
    main()