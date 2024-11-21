# Calculate Distances: Use the Haversine formula to calculate the distance between two geographic points (latitude and longitude). This will help in finding the nearest stop for each leg of the route.

# Estimate Travel Time: Calculate travel time dynamically based on distance, using a lower speed for short distances and a higher speed for longer distances. This ensures more accurate travel time estimates.

# Generate Google Maps Links: Create a Google Maps link that plots the optimized route on a map. Ensure that each stop in the route is unique to avoid duplicate waypoints.

# Optimize Route: Implement a point-to-point optimization by choosing the nearest unvisited location at each step. Organize pickups and drop-offs so that each route segment has a maximum number of stops, making the routes efficient and manageable.

# Load and Process Data: Load the data from a CSV file, preprocess it by setting default values where necessary, and convert it into a format suitable for optimization.

# Save and Export Results: Export each optimized route segment to a CSV file, including total distance, total duration, and a link to the Google Maps route. Return all Google Maps links for easy access.

# Run the Program: Execute the main function to load data, optimize the routes, and generate CSV files and map links for each route.

import math
import googlemaps

from route_optimizer import settings

def haversine(latitutde_1, longitude_1, latitude_2, longitude_2):
    # Convert to radians using formular (radians = degrees * (π / 180))
    
    latitude1_radian, longitude1_radian, latitude2_radian, longitude2_radian = map(math.radians, [latitutde_1, longitude_1, latitude_2, longitude_2])
    
    # Calculate differences
    difference_in_latitude = latitude2_radian - latitude1_radian
    difference_in_longitude = longitude2_radian - longitude1_radian

    # Calculate Haversine
    haversine = math.sin(difference_in_latitude / 2)**2 + math.cos(latitude1_radian) * math.cos(latitude2_radian) * math.sin(difference_in_longitude / 2)**2

    # Calculate distance
    distance = 2 * math.asin(math.sqrt(haversine)) * 6371.0  # Earth's radius in km is 6371.0
    
    return distance


def estimate_travel_time(distance):
    # Define speed thresholds
    short_distance_speed = 30  # km/h
    long_distance_speed = 60   # km/h
    
    # Determine travel speed based on distance
    if distance < 50:  # Assuming less than 50 km is short distance
        speed = short_distance_speed
    else:
        speed = long_distance_speed
    
    # Calculate travel time
    travel_time_hours = distance / speed
    
    return travel_time_hours


def find_nearest(current_location, locations):
        nearest_location = None
        shortest_distance = float('inf')
        
        for location in locations:
            distance = haversine(current_location['lat'], current_location['lng'], location['lat'], location['lng'])
            if distance < shortest_distance:
                shortest_distance = distance
                nearest_location = location
        
        return nearest_location, shortest_distance


def optimize_route(data):
    # Convert data to list of dictionaries
    gmaps_client = googlemaps.Client(key=settings.GOOGLE_API_KEY)
    direction_results: list = []
    locations = []
    for index, row in data.iterrows():
        if row['pickup_address_line_1'] != row['dropoff_address_1']:
            direction_results = gmaps_client.directions(
                "".join(row["pickup_lat"], row["pickup_lng"]),
                "".join(row["dropoff_lat"], row["dropoff_lng"])
            )
            
    
    # Optimize route
    total_time = 0.0
    total_distance = 0.0
    optimized_route = []
    current_location = locations.pop(0)
    
    while locations:
        nearest_location, distance = find_nearest(current_location, locations)
        optimized_route.append(nearest_location)
        locations.remove(nearest_location)
        total_distance += distance
        total_time += estimate_travel_time(distance)
        current_location = nearest_location
    
    return optimized_route, total_distance, total_time

    
def generate_google_maps_link(start_lat, start_lng, end_lat, end_lng, waypoints=None):
    
    # Waypoints (Example, add as needed)
    
    waypoints = [
        {"lat": 51.5205, "lng": -0.0884},  # Example waypoint 1
        {"lat": 51.5194, "lng": -0.0955}   # Example waypoint 2
    ]

    base_url = "https://www.google.com/maps/"
    display_map_endpoint: str = f"@?api=1&map_action=map&{waypoints}"
    # display_street_panorama_endpoint:str = f"@?api=1&map_action=pano&{parameters}"
    
    start_point = f"{start_lat},{start_lng}"
    link = base_url + start_point
    
    # Add waypoints if any
    if waypoints:
        for point in waypoints:
            link += f"/{point['lat']},{point['lng']}"
    # Add the ending point
    end_point = f"{end_lat},{end_lng}"
    link += f"/{end_point}"
    return link