import pandas as pd
import os
import logging
import time
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from tqdm import tqdm  # for progress bar
import pickle

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize geocoder
geolocator = Nominatim(user_agent="heritage_sites_merger")
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1, max_retries=3, error_wait_seconds=10)

CACHE_FILE = 'geocode_cache.pkl'

def load_geocode_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'rb') as f:
            return pickle.load(f)
    return {}

def save_geocode_cache(cache):
    with open(CACHE_FILE, 'wb') as f:
        pickle.dump(cache, f)

def safe_geocode(address, cache):
    if address in cache:
        return cache[address]
    try:
        location = geocode(address)
        cache[address] = location
        return location
    except Exception as e:
        logging.warning(f"Geocoding failed for address '{address}': {e}")
        return None

def read_and_process_csv(file_path):
    try:
        df = pd.read_csv(file_path, encoding='latin1')
    except Exception as e:
        logging.error(f"Error reading {file_path}: {e}")
        return pd.DataFrame()

    # Define common column mappings
    name_columns = ['Centrally Protected Monument', 'Name of Monument / Sites', 'Name of Monument/Site',
                   'Monuments', 'Name of the Monument', 'Monument Name', 'Heritage Site']
    city_columns = ['Areas in Delhi', 'Location', 'Locality', 'City']
    state_columns = ['State']
    address_columns = ['Address', 'Location Address']

    # Standardize column names
    df_cols = df.columns.str.strip()
    
    # Find and rename name column
    for col in name_columns:
        if col in df_cols:
            df = df.rename(columns={col: 'name'})
            break
    
    # Find and rename city column
    for col in city_columns:
        if col in df_cols:
            df = df.rename(columns={col: 'city'})
            break
    
    # Find and rename state column
    for col in state_columns:
        if col in df_cols:
            df = df.rename(columns={col: 'state'})
            break
    
    # Find and rename address column
    for col in address_columns:
        if col in df_cols:
            df = df.rename(columns={col: 'address'})
            break

    # If address column doesn't exist, create it from available information
    if 'address' not in df.columns:
        address_parts = []
        if 'name' in df.columns:
            address_parts.append(df['name'].astype(str))
        if 'city' in df.columns:
            address_parts.append(df['city'].astype(str))
        if 'state' in df.columns:
            address_parts.append(df['state'].astype(str))
        
        df['address'] = pd.Series([''] * len(df))
        for i in range(len(df)):
            parts = [part[i] for part in address_parts if part[i] != 'nan']
            df.at[i, 'address'] = ', '.join(parts)

    # Ensure all required columns exist
    required_cols = ['name', 'city', 'state', 'address']
    for col in required_cols:
        if col not in df.columns:
            df[col] = None

    return df[required_cols]

def main():
    data_dir = 'data'
    dfs = []

    # Process all CSV files in the data directory
    for filename in os.listdir(data_dir):
        if not filename.endswith('.csv'):
            continue

        file_path = os.path.join(data_dir, filename)
        logging.info(f"Processing {filename}...")
        
        df = read_and_process_csv(file_path)
        if not df.empty:
            dfs.append(df)
        else:
            logging.warning(f"No data loaded from {filename}.")

    if not dfs:
        logging.error("No data to merge. Exiting.")
        return

    merged_df = pd.concat(dfs, ignore_index=True)

    # Load or create geocode cache
    geocode_cache = load_geocode_cache()

    logging.info("Geocoding addresses... (this may take some time)")

    latitudes = []
    longitudes = []

    for address in tqdm(merged_df['address'], desc="Geocoding"):
        loc = safe_geocode(address, geocode_cache)
        if loc:
            latitudes.append(loc.latitude)
            longitudes.append(loc.longitude)
        else:
            latitudes.append(None)
            longitudes.append(None)

    merged_df['latitude'] = latitudes
    merged_df['longitude'] = longitudes

    # Save cache for next time
    save_geocode_cache(geocode_cache)

    output_path = os.path.join(data_dir, 'merged_heritage_sites.csv')
    merged_df.to_csv(output_path, index=False)
    logging.info(f"Merged data saved to {output_path}")

if __name__ == "__main__":
    main()
