import json
from pathlib import Path

from OSRM import get_all_drivers, get_all_passengers, get_route
from route_optimizer import optimize_route


BASE_DIR = Path(__file__).resolve().parent
RESULT_PATH = BASE_DIR / "result.json"

with open(RESULT_PATH, "r") as file:
    results = json.load(file)


all_drivers = get_all_drivers()
all_passengers = get_all_passengers()

drivers_dict = {
    driver["driverID"]: driver
    for driver in all_drivers
}

passengers_dict = {
    passenger["passengerID"]: passenger
    for passenger in all_passengers
}


print("\n========== ROUTE COMPARISON ==========")

for assignment in results["assignments"]:

    driver_id = assignment["driverID"]
    driver = drivers_dict[driver_id]

    assigned_passengers = [
        passengers_dict[p["passengerID"]]
        for p in assignment["assignedPassengers"]
    ]

    if not assigned_passengers:
        continue

    # Original driver route
    original_route = get_route(
        driver["startPoint"],
        driver["Destination"]
    )

    # Optimised carpool route
    optimized_route = optimize_route(
        driver,
        assigned_passengers
    )

    # Calculate additional distance and time
    extra_distance = (
        optimized_route["total_distance_km"]
        - original_route["distance_km"]
    )

    extra_time = (
        optimized_route["total_time_min"]
        - original_route["duration_min"]
    )

    print(f"\nDriver: {driver_id}")

    print("Passengers:", [
        p["passengerID"] for p in assigned_passengers
    ])

    print("\nOriginal Driver Route:")
    print("Distance:", round(original_route["distance_km"], 2), "km")
    print("Duration:", round(original_route["duration_min"], 2), "minutes")

    print("\nOptimised Carpool Route:")
    print("Sequence:", optimized_route["sequence"])
    print("Distance:", round(optimized_route["total_distance_km"], 2), "km")
    print("Duration:", round(optimized_route["total_time_min"], 2), "minutes")

    print("\nAdditional Journey:")
    print("Distance:", round(extra_distance, 2), "km")
    print("Duration:", round(extra_time, 2), "minutes")

    print("-" * 50)