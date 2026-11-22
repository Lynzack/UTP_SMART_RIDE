from OSRM import get_all_drivers, get_all_passengers
from compatibility_matrix import generate_compatibility_matrix
from GA import run_evolution, repair_genome
from pathlib import Path
import json
from route_optimizer import optimize_route
from map import visualize_optimized_route


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

    # best_population, generations = run_evolution(
    #     population_size=30,
    #     num_drivers=len(all_drivers),
    #     num_passengers=len(all_passengers),
    #     drivers=drivers,
    #     compatibility_matrix=matrix,
    #     fitness_limit=float("inf"),
    #     generation_limit=100,
    #     mutation_chance=0.5
    # )
    best_overall = None
    best_overall_fitness = -1
    best_generations = 0
    for run in range(5):

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

        best_genome, best_fitness = best_population[0]
        
        repaired = repair_genome(best_genome, drivers, matrix)

        assigned = sum(1 for gene in repaired if gene != 0)

        print(f"\n--- RUN {run + 1} ---")
        print("Best Fitness:", best_fitness)
        print("Passengers Assigned:", assigned)
        print("Generations:", generations)
        print("Best Genome:", repaired)

        if best_fitness > best_overall_fitness:
        
            best_overall = best_genome.copy()
            best_overall_fitness = best_fitness
            best_generations = generations

    best_genome = best_overall

    best_fitness = best_overall_fitness

    generations = best_generations

    repaired = repair_genome(
        best_genome,
        drivers,
        matrix
    )

    # Step 6: Optimise routes for each driver

    print("\nOptimising carpool routes...")

    optimized_routes = []

    for driver_index, driver in enumerate(all_drivers):

        assigned_passengers = []

        # Find passengers assigned to this driver
        for passenger_index, assigned_driver in enumerate(repaired):

            if assigned_driver == driver_index + 1:
                assigned_passengers.append(all_passengers[passenger_index])

        # Skip drivers without passengers
        if not assigned_passengers:
            continue

        # Optimise pickup and drop-off sequence
        optimized_route = optimize_route(
            driver,
            assigned_passengers
        )

        # Generate route map
        visualize_optimized_route(
            driver,
            assigned_passengers,
            optimized_route
        )

        optimized_routes.append({
            "driverID": driver["driverID"],
            "passengers": [
                passenger["passengerID"]
                for passenger in assigned_passengers
            ],
            "sequence": optimized_route["sequence"],
            "totalDistance": round(
                optimized_route["total_distance_km"], 2
            ),
            "totalDuration": round(
                optimized_route["total_time_min"], 2
            )
        })

        print(f'{driver["driverID"]}: Route optimised successfully.')

    

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

    # Add optimised route information
    results["optimizedRoutes"] = optimized_routes
    

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