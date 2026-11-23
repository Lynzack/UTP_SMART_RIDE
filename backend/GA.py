
from random import choices, randint, random, randrange, choice
from typing import  List, Tuple
from eligibility import is_eligible

Genome = List[int]  
Population = List[Genome]
min_compatibility = 50


def generate_genome(num_passengers : int, num_drivers : int ) -> Genome: # generate one random solution
    return choices(range(num_drivers + 1), k = num_passengers)

def generate_population(
    size,
    num_drivers,
    num_passengers,
    drivers,
    passengers,
    compatibility_matrix
):
    population = []

    for _ in range(size):

        # genome = generate_genome(
        #     num_passengers,
        #     num_drivers
        # )

        # genome = repair_genome(
        #     genome,
        #     drivers,
        #     compatibility_matrix,
        #     passengers,
        # )
        genome = generate_genome(
            num_passengers,
            num_drivers
        )

        original_genome = genome.copy()

        genome = repair_genome(
            genome,
            drivers,
            compatibility_matrix,
            passengers
        )

        if len(population) < 10:
            print("Original:", original_genome)
            print("Repaired:", genome)

        population.append(genome)

             
    return population


#Calculating fitness- how good is the solution, higher value = better solution
def fitness(genome: Genome, drivers, compatibility_matrix,passengers) :
    total_score = 0
    assigned_count = 0
    

    # driver_assignments = {
    #     driver_id :[]
    #     for driver_id in drivers
    # }
    driver_assignments = {
        driver_index + 1: []
        for driver_index in range(len(drivers))
    }

    # Step 1: Collect valid assignments
    for passenger_index, assigned_driver in enumerate(genome):

        # 0 means passenger is unassigned
        if assigned_driver == 0:
            continue

        score = compatibility_matrix[assigned_driver - 1][passenger_index]

        # Only consider compatible assignments
        if (
            score >= min_compatibility
            and is_eligible(drivers[assigned_driver - 1], passengers[passenger_index])
        ):
            driver_assignments[assigned_driver].append(
                (score, passenger_index)
            )

    # Step 2: Check driver seat capacity
    for driver_id, assignments in driver_assignments.items():

        # Prioritize passengers with higher compatibility
        assignments.sort(reverse=True)

        # available_seats = drivers[driver_id]["available_seats"]
        available_seats = drivers[driver_id - 1]["availableSeats"]

        # Keep only passengers within seat capacity
        valid_assignments = assignments[:available_seats]

        for score, passenger_index in valid_assignments:
            total_score += score
            assigned_count += 1

    # Step 3: Prioritize passenger coverage
    coverage_bonus = assigned_count * (100 * len(genome) + 1)

    return coverage_bonus + total_score


#latest
def repair_genome(genome, drivers, compatibility_matrix, passengers):

    repaired_genome = genome.copy()

    # Step 1: Remove incompatible or ineligible assignments
    for passenger_index, driver_id in enumerate(repaired_genome):

        if driver_id == 0:
            continue

        driver = drivers[driver_id - 1]
        passenger = passengers[passenger_index]

        score = compatibility_matrix[driver_id - 1][passenger_index]

        if (
            score < min_compatibility
            or not is_eligible(driver, passenger)
        ):
            repaired_genome[passenger_index] = 0

    # Step 2: Check driver seat capacities
    for driver_id, driver in enumerate(drivers, start=1):

        assigned_passengers = [
            index
            for index, assigned_driver in enumerate(repaired_genome)
            if assigned_driver == driver_id
        ]

        # Prioritise passengers with higher compatibility
        assigned_passengers.sort(
            key=lambda index: compatibility_matrix[driver_id - 1][index],
            reverse=True
        )

        available_seats = driver["availableSeats"]

        # Remove passengers exceeding available seats
        overflow_passengers = assigned_passengers[available_seats:]

        for passenger_index in overflow_passengers:
            repaired_genome[passenger_index] = 0

    return repaired_genome




def evaluate_population(population, drivers, compatibility_matrix,passengers):
    results = []
    for genome in population:
        score = fitness(genome, drivers, compatibility_matrix, passengers)
        results.append((genome, score))
    return sorted(results, key=lambda x: x[1], reverse=True)

#Select Parents
def selection_pair( evaluated_population) ->Population :
    valid_population = [
        genome_score
        for genome_score in evaluated_population
        if genome_score[1] > 0
    ]

    if len(valid_population) >= 2:
        
        parents = choices(
            population=valid_population,
            weights=[score for genome, score in valid_population],
            k=2
        )
    else :
        parents = choices(
            population=evaluated_population,
            k=2
        )

    return parents[0][0], parents[1][0]



#combine two parents to create two children
def single_point_crossover(a: Genome, b: Genome) -> Tuple[Genome, Genome]:
    if len(a) != len(b):
        raise ValueError("Genomes a and b must be of the same length")

    length = len(a)
    if length < 2:
        return a, b
    
    p = randint(1, length - 1)
    return a[0:p] + b[p:], b[0:p] + a[p:]

#random changes to genome
def mutation(genome: Genome, num_drivers: int, num: int = 1, probability: float = 1.0) -> Genome:
    for _ in range(num):
        if random() < probability:
            index = randrange(len(genome))

            possible_values = [
                driver_id
                for driver_id in range(num_drivers + 1)
                if driver_id != genome[index]
            ]

            genome[index] = choice(possible_values)

    return genome

def run_evolution(
    population_size,
    num_drivers,
    num_passengers,
    drivers,
    passengers,
    compatibility_matrix,
    fitness_limit=float("inf"),
    generation_limit=100,
    mutation_chance=0.5
):
    population = generate_population(
        population_size,
        num_drivers,
        num_passengers,
        drivers,
        passengers,
        compatibility_matrix
    )
    unique_genomes = len(set(tuple(g) for g in population))

    print("Initial unique genomes:", unique_genomes)
    print("Initial population size:", len(population))  

    for generation in range(generation_limit):

        # Evaluate and sort population
        evaluated_population = evaluate_population(
            population,
            drivers,
            compatibility_matrix,
            passengers
        )

        # Check whether fitness limit is reached
        if evaluated_population[0][1] >= fitness_limit:
            break

        # Elitism: preserve the best two chromosomes
        next_generation = [
            genome.copy()
            for genome, score in evaluated_population[:2]
        ]

        # Generate offspring
        while len(next_generation) < population_size:

            parent1, parent2 = selection_pair(evaluated_population)

            child1, child2 = single_point_crossover(
                parent1, parent2
            )

            # Apply mutation
            child1 = mutation(
                child1,
                num_drivers=num_drivers,
                probability=mutation_chance
            )

            child2 = mutation(
                child2,
                num_drivers=num_drivers,
                probability=mutation_chance
            )

            # Repair offspring after crossover and mutation
            child1 = repair_genome(
                child1,
                drivers,
                compatibility_matrix,
                passengers
            )

            child2 = repair_genome(
                child2,
                drivers,
                compatibility_matrix,
                passengers
            )


            next_generation.extend([child1, child2])

        # Keep population size consistent
        population = next_generation[:population_size]
        unique_genomes = len(set(tuple(g) for g in population))

        if generation % 50 == 0:
            print(
                f"Generation {generation}: "
                f"{unique_genomes} unique genomes"
            )

    # Final evaluation
    evaluated_population = evaluate_population(
        population,
        drivers,
        compatibility_matrix,
        passengers
    )

    return evaluated_population, generation






