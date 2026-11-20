from OSRM import get_route, get_carpool_route

def calculate_route_compatibility(driver, passenger):
    driver_route = get_route(driver["startPoint"], driver["Destination"])
    carpool_route = get_carpool_route(driver, passenger)

    detour_distance = carpool_route["distance_km"] - driver_route["distance_km"]
    detour_time = carpool_route["duration_min"] - driver_route["duration_min"]

    #calculate detour percentage
    if driver_route["distance_km"] > 0:
        detour_percentage = (
            detour_distance / driver_route["distance_km"]
        ) * 100
    else:
        detour_percentage = 0



    return {
        "detour_distance": detour_distance,
        "detour_time": detour_time,
        "detour_percentage": detour_percentage
    }