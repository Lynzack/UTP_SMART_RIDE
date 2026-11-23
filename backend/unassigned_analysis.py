from eligibility import is_eligible


def analyse_unassigned_passengers(
    results,
    all_drivers,
    all_passengers,
    matrix
):
    unassigned_ids = results["unassignedPassengers"]

    # Calculate remaining seats for each driver
    remaining_seats = {}

    for assignment in results["assignments"]:
        driver_id = assignment["driverID"]

        remaining_seats[driver_id] = (
            assignment["availableSeats"]
            - len(assignment["assignedPassengers"])
        )

    # Store analysis results
    analysis = []

    print("\n========== UNASSIGNED PASSENGER ANALYSIS ==========")

    for passenger_index, passenger in enumerate(all_passengers):

        passenger_id = passenger["passengerID"]

        if passenger_id not in unassigned_ids:
            continue

        print("\n" + "=" * 55)
        print("Passenger:", passenger_id)
        print("=" * 55)

        eligible_drivers = []
        compatible_drivers = []
        available_drivers = []
        compatibility_scores = []

        for driver_index, driver in enumerate(all_drivers):

            if not is_eligible(driver, passenger):
                continue

            driver_id = driver["driverID"]

            eligible_drivers.append(driver_id)

            score = matrix[driver_index][passenger_index]

            compatibility_scores.append({
                "driverID": driver_id,
                "score": round(float(score), 2)
            })

            print(f"  {driver_id} compatibility score: {score:.2f}")

            if score >= 50:

                compatible_drivers.append(driver_id)

                if remaining_seats.get(driver_id, 0) > 0:
                    available_drivers.append(driver_id)

        # Identify possible reason
        if not eligible_drivers:
            reason = "No eligible drivers"

        elif not compatible_drivers:
            reason = "Compatibility scores below 50"

        elif not available_drivers:
            reason = "Suitable drivers have no remaining seats"

        else:
            reason = (
                "Alternative compatible drivers exist "
                "but were not selected by GA"
            )

        print("Eligible drivers:", eligible_drivers)
        print("Compatible drivers:", compatible_drivers)
        print("Compatible drivers with available seats:", available_drivers)
        print("Possible reason:", reason)

        # Save analysis for frontend
        analysis.append({
            "passengerID": passenger_id,
            "reason": reason,
            "eligibleDrivers": eligible_drivers,
            "compatibleDrivers": compatible_drivers,
            "availableDrivers": available_drivers,
            "compatibilityScores": compatibility_scores
        })

    return analysis