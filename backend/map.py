
import folium
from OSRM import get_route


def visualize_optimized_route(driver, passengers, optimized_route):

    driver_start = driver["startPoint"]
    driver_destination = driver["Destination"]

    # Get driver's original route (without passengers)
    original_route = get_route(driver_start, driver_destination)

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
        icon=folium.Icon(color="darkred")
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

    # Original driver route (BLUE)
    original_coordinates = [
        (lat, lon)
        for lon, lat in original_route["geometry"]
    ]

    # Optimised carpool route (RED)
    route_coordinates = [
        (lat, lon)
        for lon, lat in optimized_route["geometry"]
    ]

    folium.PolyLine(
            route_coordinates,
            color="red",
            weight=5,
            opacity=0.8,
            tooltip="Optimised Carpool Route"
        ).add_to(route_map)
    

    
    

    folium.PolyLine(
            original_coordinates,
            color="blue",
            weight=5,
            opacity=0.7,
            tooltip="Original Driver Route"
        ).add_to(route_map)
    
    
    # Route legend
    legend = """
    <div style="
        position: fixed;
        bottom: 30px;
        left: 30px;
        z-index: 9999;
        background-color: white;
        padding: 10px;
        border: 2px solid grey;
        border-radius: 5px;
        font-size: 13px;
    ">
        <b>Route Legend</b><br>
        <span style="color:blue;">━━━</span> Original Driver Route<br>
        <span style="color:red;">━━━</span> Optimised Carpool Route
    </div>
    """

    route_map.get_root().html.add_child(
        folium.Element(legend)
    )

    # Adjust map zoom to include both routes and all markers
    all_coordinates = (
        original_coordinates
        + route_coordinates
        + [
            (driver_start[1], driver_start[0]),
            (driver_destination[1], driver_destination[0])
        ]
    )

    route_map.fit_bounds(all_coordinates)

    route_map.save(
        f"optimized_carpool_route_{driver['driverID']}.html"
    )

    print("Optimised carpool map saved successfully!")


