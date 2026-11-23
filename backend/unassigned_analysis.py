import json
from pathlib import Path

from OSRM import get_all_drivers, get_all_passengers
from compatibility_matrix import get_compatibility_matrix
from eligibility import is_eligible


# Load existing GA results
BASE_DIR = Path(__file__).resolve().parent

with open(BASE_DIR / "result.json", "r") as file:
    results = json.load(file)


# Retrieve datasets
all_drivers = get_all_drivers()
all_passengers = get_all_passengers()


# Generate compatibility matrix
print("Generating compatibility matrix...")
matrix = get_compatibility_matrix()


# Identify unassigned passengers
unassigned_ids = results["unassignedPassengers"]


# Calculate remaining seats for each driver
remaining_seats = {}

for assignment in results["assignments"]:

    driver_id = assignment["driverID"]

    remaining_seats[driver_id] = (
        assignment["availableSeats"]
        - len(assignment["assignedPassengers"])
    )


# Analyse unassigned passengers
print("\n========== UNASSIGNED PASSENGER ANALYSIS ==========")

for passenger_index, passenger in enumerate(all_passengers):

    if passenger["passengerID"] not in unassigned_ids:
        continue

    print("\n" + "=" * 55)
    print("Passenger:", passenger["passengerID"])
    print("=" * 55)

    eligible_drivers = []
    compatible_drivers = []
    available_drivers = []

    for driver_index, driver in enumerate(all_drivers):

        if not is_eligible(driver, passenger):
            continue

        eligible_drivers.append(driver["driverID"])

        score = matrix[driver_index][passenger_index]
        print(f"  {driver['driverID']} compatibility score: {score:.2f}")

        if score >= 50:
            compatible_drivers.append(
                (driver["driverID"], score)
            )

            if remaining_seats[driver["driverID"]] > 0:
                available_drivers.append(
                    (driver["driverID"], score)
                )

    print("Eligible drivers:", eligible_drivers)

    print("Compatible drivers (score >= 50):")

    for driver_id, score in compatible_drivers:
        print(f"  {driver_id}: {score:.2f}")

    print("Compatible drivers with available seats:")

    for driver_id, score in available_drivers:
        print(f"  {driver_id}: {score:.2f}")

    # Identify possible reason
    if not eligible_drivers:
        reason = "No eligible drivers"

    elif not compatible_drivers:
        reason = "Compatibility scores below 50"

    elif not available_drivers:
        reason = "Suitable drivers have no remaining seats"

    else:
        reason = "Alternative compatible drivers exist but were not selected by GA"

    print("\nPossible reason:", reason)

