from OSRM import get_all_drivers, get_all_passengers
from eligibility import is_eligible
from route_compatibility import calculate_route_compatibility
from fuzzy_logic import calculate_compatibility


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