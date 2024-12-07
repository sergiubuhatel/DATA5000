import pandas as pd
from geopy.geocoders import Nominatim
import folium
from folium.plugins import HeatMap
from folium import plugins
import re
import numpy as np

# Read the data
original_df = pd.read_csv('real_estate_dataset.csv', delimiter='|')

# Copy the first 10 rows to avoid modifying the original data
df = original_df.copy()

# Initialize geocoder
geolocator = Nominatim(user_agent="ottawa_real_estate", timeout=10)


# Function to geocode addresses
def geocode_address(address):
    location = geolocator.geocode(address)
    if location:
        return location.latitude, location.longitude
    else:
        return None, None


# Function to remove postal code from address
def remove_postal_code(address):
    # Regex pattern to match Canadian postal code (e.g., M5A 1A1)
    postal_code_pattern = r'\b[A-Za-z]\d[A-Za-z] \d[A-Za-z]\d\b'
    return re.sub(postal_code_pattern, '', address).strip()

def remove_apartment_number(address):
    # This pattern will match the apartment/suite number and remove it
    cleaned_address = re.sub(r'\s*#\w+\s*|\s*(?:Apt|Suite)\s*\w+\s*', '', address)

    # Strip any leading or trailing whitespace
    return cleaned_address.strip()

# Replace cities
for city in ['Carp', 'Stittsville', 'Gloucester', 'Manotick', 'Nepean', 'Greely', 'North Gower',
             'Kanata', 'Metcalfe', 'Dunrobin', 'Vars', 'Kinburn']:
    df['Address'] = df['Address'].replace(city, 'Ottawa', regex=True)

# Remove postal code and apartment number from the string
df['Address'] = df['Address'].apply(remove_postal_code)
df['Address'] = df['Address'].apply(remove_apartment_number)

# Apply geocoding to addresses
df['Coordinates'] = df['Address'].apply(geocode_address)

# Split into separate columns for latitude and longitude
df[['Latitude', 'Longitude']] = pd.DataFrame(df['Coordinates'].to_list(), index=df.index)

# Create a map centered around Ottawa's approximate coordinates
ottawa_map = folium.Map(location=[45.4215, -75.6972], zoom_start=12)

# Define the color scale using a LinearColormap
# Normalize the price column
min_price = df['Sold Price'].min()
max_price = df['Sold Price'].max()

# Create a color scale (gradient from light red to dark red)
colormap = folium.LinearColormap(
    colors=['#ffcccc', '#ff3333'],  # light red to dark red
    vmin=min_price, vmax=max_price
)

# Add markers with color based on price
for index, row in df.iterrows():
    if pd.notna(row['Latitude']) and pd.notna(row['Longitude']):
        # Normalize the price and get corresponding color from colormap
        price = row['Sold Price']
        color = colormap(price)

        # Add a circle marker for each property
        folium.CircleMarker(
            location=(row['Latitude'], row['Longitude']),
            radius=8,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.6,
            popup=f"Price: ${price:,.2f}\n{row['Address']}"
        ).add_to(ottawa_map)
    else:
        print(f"Missing coordinates for property: {row['Address']}")

# Add the color scale legend to the map
colormap.add_to(ottawa_map)

# Save the updated map
ottawa_map.save("ottawa_real_estate_colored_map_with_shades.html")