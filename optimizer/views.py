import os
import pandas as pd
import numpy as np
from django.shortcuts import render
from django.http import JsonResponse
import googlemaps
from route_optimizer import settings
from .optimize_routes import (haversine, estimate_travel_time, generate_google_maps_link, optimize_route)

# optimize_route_view:

# Loads a specific CSV file containing route data.
# Calls the optimize_routes function to generate optimized Google Maps links for each route.
# Returns these map links as a JSON response, allowing you to see all routes in Google Maps format via an API endpoint.


# data_source_table_view:

# Loads the same CSV file to display the raw data in a web template.
# If the file is missing, it shows an error message in the template.
# Passes the data to a template as a table, enabling you to view and verify the dataset used for route optimization.


def optimize_route_view(request):
    # provide your google map direction enabled api API_KEY here
    gmaps_client = googlemaps.Client(key=settings.GOOGLE_API_KEY)

    # Path to the CSV file
    data_file_path = "data/customer-requests-testingLondon36.csv"

    if not os.path.exists(data_file_path):
        return JsonResponse({"error": "CSV file not found."}, status=404)

    # Load the CSV data.
    data = pd.read_csv(data_file_path)
    data["distance"] = 0.0
    data["google_link"] = ""
    data.head()

    direction_results: list = []
    locations = []
    for index, row in data.iterrows():
        if row['pickup_address_line_1'] != row['dropoff_address_1']:
            direction_results = gmaps_client.directions("".join(row["pickup_lat"], row["pickup_lng"]), "".join(row["dropoff_lat"], row["dropoff_lng"]))
            print(f"\n DIRECTION RESULTS: {direction_results} \n")
            data.at[index, "distance"] = direction_results[0]["legs"][0]["distance"]["value"]
    
    # Optimize route
    optimized_route, total_distance, total_time = optimize_route(data)
    
    # Generate Google Maps link
    google_maps_link = generate_google_maps_link(
        optimized_route[0]['lat'], optimized_route[0]['lng'],
        optimized_route[-1]['lat'], optimized_route[-1]['lng'],
        waypoints=[{"lat": loc['lat'], "lng": loc['lng']} for loc in optimized_route[1:-1]]
    )

    context = {
        "optimized_route": optimized_route,
        "total_distance": total_distance,
        "total_time": total_time,
        "google_maps_link": google_maps_link
    }

    # Return the Google Maps link and other route details as a JSON response
    print(f"\n CONTEXT: {context} \n")
    return JsonResponse(context)


def data_source_table_view(request):
    template = "optimizer/data_source.html"
    csv_file_path = "data/customer-requests-testingLondon36.csv"

    if not os.path.exists(csv_file_path):
        context = {"error": "CSV file not found."}
        return render(request, template, context)
    
    # Load the CSV data
    data = pd.read_csv(csv_file_path)
    context = {"data": data.to_dict(orient="records")}
    
    return render(request, template, context)