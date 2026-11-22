import pandas as pd
import requests
from pathlib import Path
from eligibility import is_eligible

# from map import visualize_route

# =================================
# 1. LOAD DATASET
# =================================
BASE_DIR = Path(__file__).resolve().parent
DATASET_DIR = BASE_DIR.parent / "dataset"

locations = pd.read_csv(
    DATASET_DIR / "location.csv",
    dtype={"locationID": str}
)

drivers = pd.read_csv(
    DATASET_DIR / "driver.csv",
    dtype={"driverID": str, "UserID": str}
)

passengers = pd.read_csv(
    DATASET_DIR / "passengers.csv",
    dtype={"passengerID": str, "UserID": str}
)


# =================================
# 2. RETRIEVE LOCATION COORDINATES
# =================================

def get_coordinates(location_id):

    location = locations[
        locations["locationID"] == location_id
    ]

    if location.empty:
        raise ValueError(f"Location {location_id} not found")

    row = location.iloc[0]

    longitude = row["longitude"]
    latitude = row["latitude"]

    return longitude, latitude


# =================================
# 3. RETRIEVE DRIVER INFORMATION
# =================================

def get_driver(driver_id):

    driver = drivers[
        drivers["driverID"] == driver_id
    ]

    if driver.empty:
        raise ValueError(f"Driver {driver_id} not found")

    row = driver.iloc[0]

    origin = get_coordinates(row["startPoint"])
    destination = get_coordinates(row["Destination"])

    return {
        "driverID": driver_id,
        "UserID": row["UserID"],
        "startPoint": origin,
        "Destination": destination,
        "Date": row["Date"],
        "departureTime": row["departureTime"],
        "availableSeats": int(row["availableSeats"])
    }

def get_all_drivers ():
    driver_ids = drivers["driverID"].tolist()

    return [
        get_driver(driver_id)
        for driver_id in driver_ids
    ]


# =================================
# 4. RETRIEVE PASSENGER INFORMATION
# =================================

def get_passenger(passenger_id):

    passenger = passengers[
        passengers["passengerID"] == passenger_id
    ]

    if passenger.empty:
        raise ValueError(f"Passenger {passenger_id} not found")

    row = passenger.iloc[0]

    origin = get_coordinates(row["startPoint"])
    destination = get_coordinates(row["Destination"])

    return {
        "passengerID": passenger_id,
        "UserID": row["UserID"],
        "startPoint": origin,
        "Destination": destination,
        "Date": row["Date"],
        "preferredTime": row["preferredTime"]
    }

def get_all_passengers ():
    passenger_ids = passengers["passengerID"].tolist()
    return [
        get_passenger(passenger_id)
        for passenger_id in passenger_ids
    ]


# =================================
# 5. CALCULATE ROUTE USING OSRM
# =================================

def get_route(start, destination):

    base_url = "https://router.project-osrm.org"

    url = (
        f"{base_url}/route/v1/driving/"
        f"{start[0]},{start[1]};"
        f"{destination[0]},{destination[1]}"
    )

    response = requests.get(
    url,
    params={
        "overview": "full",
        "geometries": "geojson"
    }
)
    response.raise_for_status()

    data = response.json()

    if data["code"] != "Ok":
        raise ValueError(f"OSRM error: {data['code']}")

    route = data["routes"][0]

    return {
        "distance_km": route["distance"] / 1000,
        "duration_min": route["duration"] / 60,
        "geometry": route["geometry"]["coordinates"]
    }

def get_carpool_route(driver, passenger):

    base_url = "https://router.project-osrm.org"

    coordinates = [
        driver["startPoint"],
        passenger["startPoint"],
        passenger["Destination"],
        driver["Destination"]
    ]

    coordinate_string = ";".join(
        f"{lon},{lat}" for lon, lat in coordinates
    )

    url = f"{base_url}/route/v1/driving/{coordinate_string}"

    response = requests.get(
        url,
        params={
            "overview": "full",
            "geometries": "geojson"
        }
    )

    response.raise_for_status()
    data = response.json()

    if data["code"] != "Ok":
        raise ValueError(f"OSRM error: {data['code']}")

    route = data["routes"][0]

    return {
        "distance_km": route["distance"] / 1000,
        "duration_min": route["duration"] / 60,
        "geometry": route["geometry"]["coordinates"]
    }

def get_multi_passenger_route(driver, passengers):

    coordinates = [
        driver["startPoint"]
    ]

    for passenger in passengers:
        coordinates.append(passenger["startPoint"])
        coordinates.append(passenger["Destination"])

    coordinates.append(driver["Destination"])

    # Calculate the complete route using OSRM
    # We will implement this part next.

def get_multi_stop_route(coordinates):

    base_url = "https://router.project-osrm.org"

    coordinate_string = ";".join(
        f"{lon},{lat}"
        for lon, lat in coordinates
    )

    url = f"{base_url}/route/v1/driving/{coordinate_string}"

    response = requests.get(
        url,
        params={
            "overview": "full",
            "geometries": "geojson"
        }
    )

    response.raise_for_status()

    data = response.json()

    if data["code"] != "Ok":
        raise ValueError(f"OSRM error: {data['code']}")

    route = data["routes"][0]

    return {
        "distance_km": route["distance"] / 1000,
        "duration_min": route["duration"] / 60,
        "geometry": route["geometry"]["coordinates"]
    }


def get_travel_time_matrix(coordinates):

    base_url = "https://router.project-osrm.org"

    coordinate_string = ";".join(
        f"{lon},{lat}"
        for lon, lat in coordinates
    )

    url = f"{base_url}/table/v1/driving/{coordinate_string}"

    response = requests.get(
        url,
        params={
            "annotations": "duration"
        }
    )

    response.raise_for_status()

    data = response.json()

    if data["code"] != "Ok":
        raise ValueError(f"OSRM error: {data['code']}")

    return [
        [
            duration / 60 if duration is not None else float("inf")
            for duration in row
        ]
        for row in data["durations"]
    ]