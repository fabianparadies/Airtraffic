import pandas as pd
import numpy as np
import requests
from geopy.distance import geodesic
import os

OPENFLIGHTS_URL = "https://raw.githubusercontent.com/jpatokal/openflights/master/data/airlines.dat"

OPENSKY_API = "https://opensky-network.org/api/states/all"

# ==============================================================================================================
# ==============================================================================================================
# FUNCTIONS
# ==============================================================================================================
# ==============================================================================================================
    

# Load airport data
def loadAirports():
    print("Loading airport data...")  # Debug feedback
    #url = r"https://ourairports.com/data/airports.csv"
    url = "/Users/fabianparadies/Documents/GitHub/Airtraffic/airports.csv"
    df_airports = pd.read_csv(url, sep=",")
    df_airports = df_airports[['ident', 'name', 'latitude_deg', 'longitude_deg', 'type']]
    df_airports = df_airports[df_airports['type'] == 'large_airport']  # Filter large airports
    print(f"Loaded {len(df_airports)} large airports.")  # Feedback
    return df_airports


# Fetch airline data for dropdown
def get_airlines():
    """
    Purpose: Fetches and processes airline metadata from the OpenFlights dataset.

    Key Steps:
    - Downloads airline data with fixed column names.
    - Filters active airlines with a valid ICAO code.
    - Removes duplicates by ICAO.
    - Constructs a readable label for dropdowns: "Airline Name - ICAO".
    - Returns a simplified dataframe: ["ICAO", "Airline", "Country"].
    """
    print("Fetching airline data from OpenFlights...")  # Feedback

    try:
        # Define column names for OpenFlights dataset
        columnNames = ["AirlineID", "Name", "Alias", "IATA", "ICAO", "Callsign", "Country", "Active"]

        # Load airline data from OpenFlights
        df_airlines = pd.read_csv(
            OPENFLIGHTS_URL,
            header=None,
            names=columnNames,
            usecols=["Name", "ICAO", "Country", "Active"]
        )

        print(f"Fetched {len(df_airlines)} airlines (before filtering).")  # Feedback

        # Filter active airlines and those with a valid ICAO code
        df_airlines = df_airlines[(df_airlines['Active'] == 'Y') & (df_airlines["ICAO"].notna())]

        # Remove duplicates based on ICAO code
        df_airlines = df_airlines.drop_duplicates(subset=["ICAO"])

        # Create concatenated column for dropdown
        df_airlines["Airline"] = df_airlines["Name"] + " - " + df_airlines["ICAO"]

        df_airlines = df_airlines[["ICAO", 'Name', "Airline", "Country"]].sort_values(by="Name").reset_index(drop=True)

        print(f"Returning {len(df_airlines)} active airlines with ICAO codes.")  # Feedback
        return df_airlines[["ICAO", "Name", "Airline", "Country"]]

    except Exception as e:
        print(f"Error loading OpenFlights data: {e}")
        return pd.DataFrame(columns=columnNames)


def fetch_flightdata():
    """
    Purpose: Queries the OpenSky API for real-time flight state data within a specified bounding box (Central Europe in this case).

    Key Points:
    - Uses geographic coordinates (lamin, lamax, lomin, lomax) to limit results.
    - Returns the raw JSON response if the request is successful.
    - Prints error messages on failure.
    """
    print("Requesting flight data from OpenSky...")  # Feedback
    flightsdata = []

    params_eu = {
        "lamin": 35.0,
        "lamax": 72.0,
        "lomin": -10.0,
        "lomax": 30.0
    }

    params_central_europe = {
        "lamin": 45,
        "lamax": 55,
        "lomin": 5.0,
        "lomax": 20.0
    }

    params_ge = {
        "lamin": 47.2,
        "lamax": 55.1,
        "lomin": 5.9,
        "lomax": 15.0
    }

    try:
        response = requests.get(OPENSKY_API, params=params_eu)
        if response.status_code == 200:
            print("Flight data fetched successfully.")  # Feedback
            return response.json()
        else:
            print(f"Error: {response.status_code} - {response.text}")
        return None

    except Exception as e:
        print(f"An error occurred: {e}")
        return None


# Convert Unix timestamp to human-readable hour format
def convert_TimestamptoHour(unix):
    """
    Purpose: Converts Unix timestamps into human-readable UTC time in HH:MM:SS format.

    Usage:
    - Primarily used to display time-related flight data like time_position.
    """
    from datetime import datetime, timezone
    if pd.notna(unix):
        return datetime.fromtimestamp(int(unix), tz=timezone.utc).strftime('%H:%M:%S')

"""
def process_flightdata_selectedAirline(selectedAirlineCode):
    
    Purpose: Processes the raw OpenSky flight data and filters it by the selected airline's ICAO code.

    Workflow:
    - Calls fetch_flightdata() to get flight data.
    - Converts it into a DataFrame with known columns.
    - Filters by the callsign using filter_by_airlines().
    - (Commented out) Optionally identifies the nearest airport for each flight.
    - Converts timestamps to readable format.
    - Renames columns for clarity (origin_country → departing_from, etc.).
    - Returns a cleaned DataFrame with selected columns ready for display.

    Returned Columns: icao24, callsign, departing_from, time_at_Position, longitude, latitude,

    print(f"Processing flight data for airline: {selectedAirlineCode}")  # Feedback

    # Load airport data
    df_airports = loadAirports()

    # Fetch OpenSky flight data
    flightsdata = fetch_flightdata()

    if flightsdata and "states" in flightsdata:
        print(f"Number of flight records fetched: {len(flightsdata['states'])}")  # Feedback

        # Define columns and create DataFrame
        columns = [
            "icao24", "callsign", "origin_country", "time_position", "last_contact",
            "longitude", "latitude", "baro_altitude", "on_ground", "velocity",
            "true_track", "vertical_rate", "sensors", "geo_altitude", "squawk",
            "spi", "position_source"
        ]

        df_flights = pd.DataFrame(flightsdata["states"], columns=columns)
        print(f"Raw flights dataframe shape: {df_flights.shape}")  # Feedback

        # Filter by selected airline
        df_filtered_flights = filter_by_airlines(df_flights, selectedAirlineCode).dropna(subset=["latitude", "longitude"]).copy()
        print(f"Filtered flights count: {len(df_filtered_flights)}")  # Feedback

        # Find nearest airport for each flight
        print("Finding nearest airports for each flight...")  # Feedback
        df_filtered_flights["nearest_airport"] = df_filtered_flights.apply(
            lambda row: nearest_airport(row["latitude"], row["longitude"], df_airports)[0]
            if pd.notna(row["latitude"]) and pd.notna(row["longitude"]) else None,
            axis=1
        )

        # Convert timestamps to readable time
        print("Converting timestamps...")  # Feedback
        df_filtered_flights["timePosition"] = df_filtered_flights["time_position"].apply(convert_TimestamptoHour)

        # Convert speed from m/s to km/h
        if "velocity" in df_new_flights.columns:
            df_new_flights["speed_Kmh"] = df_new_flights["velocity"] * 3.6


        # Rename columns
        columnRenameMap = {
            "origin_country": "country_icao",
            "timePosition": "time_at_position",
            "baro_altitude": "altitude",
            "velocity": "speed_kmh",
            "nearest_airport": "located_at"
        }
        df_filtered_flights.rename(columns=columnRenameMap, inplace=True)

        # Select specific columns for output
        display_columns = [
            "icao24", "callsign", "country_icao", "time_at_position",
            "longitude", "latitude", "altitude", "on_ground", "speed_kmh",
            "true_track", "vertical_rate", "geo_altitude", 
            "spi", "located_at"
        ]

        print("Flight data processing complete.\n")  # Feedback
        return df_filtered_flights.reset_index(drop=True)

    else:
        print("No flight data available or error fetching data.")  # Feedback
        return pd.DataFrame()
"""

def process_flightdata():
    """
    Purpose: Processes the raw OpenSky flight data and filters it by the selected airline's ICAO code.

    Workflow:
    - Calls fetch_flightdata() to get flight data.
    - Converts it into a DataFrame with known columns.
    - Filters by the callsign using filter_by_airlines().
    - (Commented out) Optionally identifies the nearest airport for each flight.
    - Converts timestamps to readable format.
    - Renames columns for clarity (origin_country → departing_from, etc.).
    - Returns a cleaned DataFrame with selected columns ready for display.
    """
    
    # Load airport data
    df_airports = loadAirports()

    # Fetch OpenSky flight data
    flightsdata = fetch_flightdata()

    if flightsdata and "states" in flightsdata:
        print(f"Number of flight records fetched: {len(flightsdata['states'])}")  # Feedback

        # Define columns and create DataFrame
        columns = [
            "icao24", "callsign", "origin_country", "time_position", "last_contact",
            "longitude", "latitude", "baro_altitude", "on_ground", "velocity",
            "true_track", "vertical_rate", "sensors", "geo_altitude", "squawk",
            "spi", "position_source"
        ]

        df_new_flights = pd.DataFrame(flightsdata["states"], columns=columns)
        print(f"Raw flights dataframe shape: {df_new_flights.shape}")  # Feedback

        # Find nearest airport for each flight
        print("Finding nearest airports for each flight...")  # Feedback
        df_new_flights["nearest_airport"] = df_new_flights.apply(
            lambda row: nearest_airport(row["latitude"], row["longitude"], df_airports)[0]
            if pd.notna(row["latitude"]) and pd.notna(row["longitude"]) else None,
            axis=1
        )

        # Convert timestamps to readable time
        print("Converting timestamps...")  # Feedback
        df_new_flights["time_at_position"] = df_new_flights["time_position"].apply(convert_TimestamptoHour)

        # Convert speed from m/s to km/h
        if "velocity" in df_new_flights.columns:
            df_new_flights["velocity"] = df_new_flights["velocity"] * 3.6

        # Rename columns
        columnRenameMap = {
            "origin_country": "country_icao",
            "timePosition": "time_at_position",
            "baro_altitude": "altitude",
            "velocity": "speed_kmh",
            "nearest_airport": "located_at"
        }
        
        df_new_flights.rename(columns=columnRenameMap, inplace=True)


        # Select specific columns for output
        display_columns = [
            "icao24", "callsign", "country_icao", "time_at_position",
            "longitude", "latitude", "altitude", "on_ground", "speed_kmh",
            "true_track", "vertical_rate", "geo_altitude", 
            "spi", "located_at"
        ]

        print("Flight data processing complete.\n")  # Feedback
        return df_new_flights[display_columns].reset_index(drop=True)
    
    else:
        print("No flight data available or error fetching data.")  # Feedback
        return pd.DataFrame()


def filter_by_airlines(df_flights, airline_code):
    """
    Purpose: Filters the flights DataFrame to include only those flights that start with a given ICAO airline code in the callsign.

    Details:
    - Cleans up whitespace in callsign.
    - Returns only rows that start with the specified airline code (case-sensitive).
    """
    print(f"Filtering flights by airline code: {airline_code}")  # Feedback
    df_flights = df_flights.copy()
    df_flights.loc[:, "callsign"] = df_flights["callsign"].str.strip()
    return df_flights[df_flights["callsign"].str.startswith(airline_code, na=False)]


def nearest_airport(lat, lon, airports):
    """
    Purpose: Given a location (lat, lon), finds the nearest large airport using geodesic distance.

    How it works:
    - Uses the geopy library to calculate distances.
    - Returns the name, ICAO identifier, and distance to the closest airport.

    Find the nearest airports to a given latitude and longitude.

    :param lat: Latitude of the location.
    :param lon: Longitude of the location.
    :param airports
    """
    flight_position = (lat, lon)
    distances = airports.apply(
        lambda row: geodesic(flight_position, (row['latitude_deg'], row['longitude_deg'])).kilometers,
        axis=1
    )
    nearestIndex = distances.idxmin()
    nearestAirport = airports.loc[nearestIndex]
    return nearestAirport['name'], nearestAirport['ident'], distances[nearestIndex]

# ==============================================================================================================
# ==============================================================================================================
# ==============================================================================================================

# Fetch airlines
df_airlines = get_airlines()
df_airlines.to_csv("/Users/fabianparadies/Documents/GitHub/Airtraffic/data_airlines.csv", index=False)

# Process flight data
df_new_flights = process_flightdata()
df_new_flights.head()  # Display the first few rows for verification

# Save the new flight data to a CSV file
output_path = "/Users/fabianparadies/Documents/GitHub/Airtraffic/data_flights.csv"

# Load existing data if the file exists
if os.path.exists(output_path):
    try:
        df_old_flights = pd.read_csv(output_path, sep = ",", encoding="utf-8")
        df_old_flights.head()
    except Exception as e:
        print(f"Warning: {output_path} is not valid CSV. Starting fresh. Error: {e}")
        df_old_flights = pd.DataFrame()
else:
    df_old_flights = pd.DataFrame()

# Append new flights to old data
df_combined_flights = pd.concat([df_old_flights, df_new_flights], ignore_index=True)
df_combined_flights.head()  # Display the first few rows for verification

# Save the combined list back to the JSON file
df_combined_flights.to_csv("/Users/fabianparadies/Documents/GitHub/Airtraffic/data_flights.csv", index=False, encoding="utf-8")