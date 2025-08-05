import pandas as pd
import numpy as np
import requests
from geopy.distance import geodesic

OPENFLIGHTS_URL = "https://raw.githubusercontent.com/jpatokal/openflights/master/data/airlines.dat"

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

df_airlines = df_airlines[["ICAO", "Name", "Airline", "Country"]].sort_values(by="Name").reset_index(drop=True)

print(f"Returning {len(df_airlines)} active airlines with ICAO codes.")  # Feedback