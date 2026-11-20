import folium

def visualize_route(driver, passenger, driver_route, carpool_route):

    start = driver["startPoint"]

    route_map = folium.Map(
        location=[start[1], start[0]],
        zoom_start=13
    )

    # Driver origin
    folium.Marker(
        [start[1], start[0]],
        popup="Driver Origin",
        icon=folium.Icon(color="green")
    ).add_to(route_map)

    # Driver destination
    folium.Marker(
        [driver["Destination"][1], driver["Destination"][0]],
        popup="Driver Destination",
        icon=folium.Icon(color="red")
    ).add_to(route_map)

    # Passenger pickup
    folium.Marker(
        [passenger["startPoint"][1], passenger["startPoint"][0]],
        popup="Passenger Pickup",
        icon=folium.Icon(color="blue")
    ).add_to(route_map)

    # Passenger drop-off
    folium.Marker(
        [passenger["Destination"][1], passenger["Destination"][0]],
        popup="Passenger Drop-off",
        icon=folium.Icon(color="purple")
    ).add_to(route_map)

    # Driver's original route
    route_coordinates = [
        (lat, lon)
        for lon, lat in driver_route["geometry"]
    ]

    folium.PolyLine(
        route_coordinates,
        color="blue",
        weight=5,
        tooltip="Driver Original Route"
    ).add_to(route_map)

    folium.PolyLine(
    [(lat, lon) for lon, lat in carpool_route["geometry"]],
    color="red",
    weight=5,
    tooltip="Alternative Carpool Route"
).add_to(route_map)

    route_map.save("driver_route_map.html")

    print("Map saved successfully!")


