from OSRM import get_all_drivers, get_all_passengers
from compatibility_matrix import generate_compatibility_matrix
from GA import run_evolution, repair_genome
from pathlib import Path
import json


min_compatibility = 60

def prepare_results(best_genome, all_drivers, all_passengers, matrix):

    assignments = []
    unassigned = []

    # Go through every driver
    for driver_index, driver in enumerate(all_drivers, start=1):

        assigned_passengers = []

        # Find passengers assigned to this driver
        for passenger_index, assigned_driver in enumerate(best_genome):

            if assigned_driver != driver_index:
                continue

            score = matrix[driver_index - 1][passenger_index]

            if score >= min_compatibility:

                assigned_passengers.append({
                    "passengerID": all_passengers[passenger_index]["passengerID"],
                    "compatibility": round(score, 2)
                })

        assignments.append({
            "driverID": driver["driverID"],
            "availableSeats": driver["availableSeats"],
            "assignedPassengers": assigned_passengers
        })

    # Identify assigned passengers
    assigned_ids = [
        passenger["passengerID"]
        for driver in assignments
        for passenger in driver["assignedPassengers"]
    ]

    # Identify unassigned passengers
    for passenger in all_passengers:

        if passenger["passengerID"] not in assigned_ids:
            unassigned.append(passenger["passengerID"])

    return {
        "status": "success",
        "totalDrivers": len(all_drivers),
        "totalPassengers": len(all_passengers),
        "totalAssigned": len(assigned_ids),
        "totalUnassigned": len(unassigned),
        "assignments": assignments,
        "unassignedPassengers": unassigned
    }

    
def main():

    # Step 1: Retrieve drivers and passengers
    all_drivers = get_all_drivers()
    all_passengers = get_all_passengers()

    # Step 2: Generate compatibility matrix
    print("Generating compatibility matrix...")

    matrix = generate_compatibility_matrix()

    # Step 3: Prepare driver information for GA
    drivers = {
        index: {
            "available_seats": driver["availableSeats"]
        }
        for index, driver in enumerate(all_drivers, start=1)
    }

    # Step 4: Run Genetic Algorithm
    print("Running Genetic Algorithm...")

    best_population, generations = run_evolution(
        population_size=30,
        num_drivers=len(all_drivers),
        num_passengers=len(all_passengers),
        drivers=drivers,
        compatibility_matrix=matrix,
        fitness_limit=float("inf"),
        generation_limit=100,
        mutation_chance=0.5
    )

    # Step 5: Retrieve best genome
    best_genome, best_fitness = best_population[0]

    # Step 6: Repair best genome
    repaired = repair_genome(
        best_genome,
        drivers,
        matrix
    )

    # Step 7: Prepare final results
    results = prepare_results(
        repaired,
        all_drivers,
        all_passengers,
        matrix
    )

    # Add GA information
    results["bestFitness"] = round(best_fitness, 2)
    results["generations"] = generations

    # Step 8: Export JSON
    output_path = Path(__file__).resolve().parent / "result.json"

    with open(output_path, "w") as file:
        json.dump(results, file, indent=4)

    print("\n--- MATCHING RESULTS ---")
    print("Total assigned:", results["totalAssigned"])
    print("Total unassigned:", results["totalUnassigned"])
    print("Best fitness:", results["bestFitness"])

    print(f"\nResults exported to: {output_path}")

if __name__ == "__main__":
    main()