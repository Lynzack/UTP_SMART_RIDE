import folium



def visualize_optimized_route(driver, passengers, optimized_route):

    driver_start = driver["startPoint"]
    driver_destination = driver["Destination"]

    # Create map
    route_map = folium.Map(
        location=[driver_start[1], driver_start[0]],
        zoom_start=13
    )

    # Driver origin
    folium.Marker(
        [driver_start[1], driver_start[0]],
        popup="Driver Origin",
        icon=folium.Icon(color="green")
    ).add_to(route_map)

    # Driver destination
    folium.Marker(
        [driver_destination[1], driver_destination[0]],
        popup="Driver Destination",
        icon=folium.Icon(color="red")
    ).add_to(route_map)

    # Passenger markers
    for passenger in passengers:

        passenger_id = passenger["passengerID"]

        pickup = passenger["startPoint"]
        dropoff = passenger["Destination"]

        # Pickup marker
        folium.Marker(
            [pickup[1], pickup[0]],
            popup=f"{passenger_id} Pickup",
            icon=folium.Icon(color="blue")
        ).add_to(route_map)

        # Drop-off marker
        folium.Marker(
            [dropoff[1], dropoff[0]],
            popup=f"{passenger_id} Drop-off",
            icon=folium.Icon(color="purple")
        ).add_to(route_map)

    # Optimised carpool route
    route_coordinates = [
        (lat, lon)
        for lon, lat in optimized_route["geometry"]
    ]

    folium.PolyLine(
        route_coordinates,
        color="red",
        weight=5,
        tooltip="Optimised Carpool Route"
    ).add_to(route_map)

    # Adjust map zoom
    all_coordinates = route_coordinates + [
        (driver_start[1], driver_start[0]),
        (driver_destination[1], driver_destination[0])
    ]

    route_map.fit_bounds(all_coordinates)

    route_map.save(
        f"optimized_carpool_route_{driver['driverID']}.html"
    )

    print("Optimised carpool map saved successfully!")