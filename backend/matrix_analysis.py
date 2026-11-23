
from OSRM import get_all_drivers, get_all_passengers
from compatibility_matrix import get_compatibility_matrix
from eligibility import is_eligible

# Minimum compatibility threshold
MIN_COMPATIBILITY = 50

drivers = get_all_drivers()
passengers = get_all_passengers()
matrix = get_compatibility_matrix()

print("\n========== COMPATIBILITY MATRIX ANALYSIS ==========")

total_candidates = 0
no_candidates = []

for passenger_index, passenger in enumerate(passengers):

    suitable_drivers = []

    for driver_index, driver in enumerate(drivers):

        eligible = is_eligible(driver, passenger)
        score = matrix[driver_index][passenger_index]

        if eligible and score >= MIN_COMPATIBILITY:
            suitable_drivers.append({
                "driverID": driver["driverID"],
                "score": round(score, 2)
            })

    total_candidates += len(suitable_drivers)

    print(f"\nPassenger: {passenger['passengerID']}")
    print(f"Suitable drivers: {len(suitable_drivers)}")

    for driver in suitable_drivers:
        print(
            f"  {driver['driverID']}: "
            f"Compatibility = {driver['score']}"
        )

    if not suitable_drivers:
        no_candidates.append(passenger["passengerID"])

print("\n========== SUMMARY ==========")
print("Total drivers:", len(drivers))
print("Total passengers:", len(passengers))
print("Minimum compatibility:", MIN_COMPATIBILITY)
print("Total suitable driver options:", total_candidates)
print("Passengers with no suitable drivers:", len(no_candidates))
print("Passenger IDs:", no_candidates)
print(get_compatibility_matrix())
