from OSRM import get_all_drivers, get_all_passengers
from eligibility import is_eligible
from route_compatibility import calculate_route_compatibility
from fuzzy_logic import calculate_compatibility

import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
CACHE_PATH = BASE_DIR / "matrix_cache.json"


def get_compatibility_matrix():

    if CACHE_PATH.exists():

        try:
            with open(CACHE_PATH, "r") as file:
                matrix = json.load(file)

            # Validate matrix dimensions
            if (
                isinstance(matrix, list)
                and len(matrix) == len(get_all_drivers())
                and all(isinstance(row, list) for row in matrix)
                and all(len(row) == len(get_all_passengers()) for row in matrix)
            ):
                print("Loading saved compatibility matrix...")
                return matrix

            print("Invalid matrix dimensions. Regenerating cache.")

        except (json.JSONDecodeError, ValueError):
            print("Cache file is empty or corrupted.")

    print("Generating new compatibility matrix...")

    matrix = generate_compatibility_matrix()

    with open(CACHE_PATH, "w") as file:
        json.dump(matrix, file, indent=4)

    print("Compatibility matrix saved!")

    return matrix

def generate_compatibility_matrix():

    all_drivers = get_all_drivers()
    all_passengers = get_all_passengers()

    matrix = []

    for driver in all_drivers:

        driver_scores = []

        for passenger in all_passengers:

            if is_eligible(driver, passenger):

                try:
                    result = calculate_route_compatibility(
                        driver, passenger
                    )

                    score = calculate_compatibility(
                        result["detour_distance"],
                        result["detour_time"],
                        result["detour_percentage"]
                    )

                    
                except Exception as error:
                    print(
                        f'Error: {driver["driverID"]} - '
                        f'{passenger["passengerID"]}: {error}'
                    )

                    score = 0

            else:
                score = 0

            driver_scores.append(float(score))

        matrix.append(driver_scores)

    return [
        [float(score) for score in row]
        for row in matrix
    ]

