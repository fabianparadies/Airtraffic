# import necessary libraries
import pandas as pd
import requests
from pandas import json_normalize
import json
import os

# The columns are based on the structure of the Global Airport Database
global_airports = pd.read_csv("/Users/fabianparadies/Documents/GitHub/Airtraffic/GlobalAirportDatabase.txt", sep = ":", header = None)

# Define the column names for the DataFrame
global_airports.columns = [
    "ICAO_Code",
    "IATA_Code",
    "Airport_Name",
    "City_Town",
    "Country",
    "Lat_Degrees",
    "Lat_Minutes",
    "Lat_Seconds",
    "Lat_Direction",
    "Long_Degrees",
    "Long_Minutes",
    "Long_Seconds",
    "Long_Direction",
    "Altitude_Meters",
    "Latitude_Decimal",
    "Longitude_Decimal"
]

# Filter for European airports based on IATA codes
# Here, we are using a small subset of European airports for demonstration purposes
europe_airports = global_airports[global_airports['IATA_Code'].str.lower().isin([
    "lhr", "cdg"
])]


# API flitghts
# Initialize an empty list to collect all flights
all_flights = []

# Loop through each IATA code to fetch flight data
for iata in europe_airports["IATA_Code"].unique():
  params = {
    "access_key": "04fd53732de6a34e2aaad028fe31d9d2",
    "dep_iata": iata
  }

  print(f"Fetching flights for {iata}", flush=True)
    
# Make the API request to fetch flight data
  api_flights_response = requests.get("https://api.aviationstack.com/v1/flights", params)

# Check if the API request was successful
  if api_flights_response.status_code != 200:
      print(f"{iata}: Error during loading – Status {api_flights_response.status_code}", flush=True)
      continue

# Parse the JSON response
  api_flights_result = api_flights_response.json()
  
  print(f"{iata} API response keys: {api_flights_result.keys()}", flush=True)

# Extract the flight data from the response 
  data_flights = api_flights_result["data"]

# Collect all flights in a single list
  all_flights.extend(data_flights) 

  print(f"{iata}: {len(data_flights)} Flights received", flush=True)

print(f"Collected: {len(all_flights)}", flush=True)


output_path = "/Users/fabianparadies/Documents/GitHub/Airtraffic/flights.json"

# Load existing data if the file exists
if os.path.exists(output_path):
    try:
        with open(output_path, "r", encoding="utf-8") as f:
            old_flights = json.load(f)
    except json.JSONDecodeError:
        print("Warning: flights.json is not valid JSON. Starting fresh.")
        old_flights = []
else:
    old_flights = []

# Append new flights to old data
combined_flights = old_flights + all_flights

# Save the combined list back to the JSON file
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(combined_flights, f, indent=2, ensure_ascii=False)