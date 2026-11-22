from itertools import permutations
from OSRM import get_travel_time_matrix, get_multi_stop_route

def generate_valid_sequences(passengers):

    passenger_ids = [
        passenger["passengerID"]
        for passenger in passengers
    ]

    stops = []

    for passenger_id in passenger_ids:
        stops.append(f"{passenger_id}_PICKUP")
        stops.append(f"{passenger_id}_DROPOFF")

    valid_sequences = []

    for sequence in permutations(stops):

        valid = True

        for passenger_id in passenger_ids:

            pickup = sequence.index(f"{passenger_id}_PICKUP")
            dropoff = sequence.index(f"{passenger_id}_DROPOFF")

            if pickup > dropoff:
                valid = False
                break

        if valid:
            valid_sequences.append(sequence)

    return valid_sequences

def optimize_route(driver, passengers):

    if not passengers:
        raise ValueError("No passengers assigned to this driver.")

    # Generate all valid pickup and drop-off sequences
    sequences = generate_valid_sequences(passengers)

    # Map passenger IDs to passenger information
    passenger_dict = {
        passenger["passengerID"]: passenger
        for passenger in passengers
    }

    # Starting point
    coordinates = [driver["startPoint"]]

    # Add all passenger pickup and drop-off locations
    for passenger in passengers:
        coordinates.append(passenger["startPoint"])
        coordinates.append(passenger["Destination"])

    # Final destination
    coordinates.append(driver["Destination"])

    # Generate travel-time matrix
    time_matrix = get_travel_time_matrix(coordinates)

    best_sequence = None
    shortest_time = float("inf")

    # Evaluate every valid sequence
    for sequence in sequences:

        current_time = 0
        current_location = 0

        for stop in sequence:

            passenger_id, stop_type = stop.rsplit("_", 1)

            passenger = passenger_dict[passenger_id]

            if stop_type == "PICKUP":
                next_location = coordinates.index(
                    passenger["startPoint"]
                )
            else:
                next_location = coordinates.index(
                    passenger["Destination"]
                )

            current_time += time_matrix[current_location][next_location]

            current_location = next_location

        # Travel from final passenger stop to driver destination
        current_time += time_matrix[current_location][-1]

        if current_time < shortest_time:
            shortest_time = current_time
            best_sequence = sequence

    # Construct the coordinates in the optimised order
    optimized_coordinates = [driver["startPoint"]]

    for stop in best_sequence:

        passenger_id, stop_type = stop.rsplit("_", 1)

        passenger = passenger_dict[passenger_id]

        if stop_type == "PICKUP":
            optimized_coordinates.append(passenger["startPoint"])
        else:
            optimized_coordinates.append(passenger["Destination"])

    optimized_coordinates.append(driver["Destination"])

    # Retrieve actual road route
    route = get_multi_stop_route(optimized_coordinates)

    return {
        "sequence": list(best_sequence),
        "total_time_min": route["duration_min"],
        "total_distance_km": route["distance_km"],
        "geometry": route["geometry"],
        "coordinates": optimized_coordinates
    }

