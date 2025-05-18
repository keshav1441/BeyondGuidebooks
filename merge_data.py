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

def read_and_process_csv(file_path, rename_map, fixed_cols=None, extra_cols=None, state=None, city=None):
    try:
        df = pd.read_csv(file_path, encoding='latin1')
    except Exception as e:
        logging.error(f"Error reading {file_path}: {e}")
        return pd.DataFrame()

    # Rename columns safely if they exist
    for old_col, new_col in rename_map.items():
        if old_col in df.columns:
            df = df.rename(columns={old_col: new_col})
        else:
            logging.warning(f"Expected column '{old_col}' not found in {file_path}")

    # Add fixed columns like state, city if provided
    if state:
        df['state'] = state
    if city:
        df['city'] = city
    if extra_cols:
        for col, val in extra_cols.items():
            df[col] = val

    # Build the address column safely
    address_parts = []
    for col in ['site_name', 'city', 'district', 'state']:
        if col in df.columns:
            address_parts.append(df[col].astype(str))
    df['address'] = pd.Series([''] * len(df))
    for i in range(len(df)):
        parts = [part[i] for part in address_parts if part[i] != 'nan']
        df.at[i, 'address'] = ', '.join(parts)

    # Select columns present in the DataFrame for final output
    output_cols = ['site_name', 'address']
    for c in ['city', 'state']:
        if c in df.columns:
            output_cols.append(c)

    return df[output_cols]

def main():
    data_dir = 'data'
    files_info = {
        'Heritage_Delhi.csv': {
            'rename_map': {'Centrally Protected Monument': 'site_name', 'Areas in Delhi': 'city'},
            'state': 'Delhi'
        },
        'Rajya_Sabha_Session_234_AU2266_4.csv': {
            'rename_map': {'Name of Monument / Sites': 'site_name', 'Location': 'city', 'District': 'district'},
            'state': 'West Bengal'
        },
        'rs_session-237_AU2747_1.2.csv': {
            'rename_map': {'Name of Monument/Site': 'site_name', 'Locality': 'city', 'District': 'district'},
            'state': 'Punjab'
        },
        'RS_Session_255_AU_2232_2.csv': {
            'rename_map': {'Monuments': 'site_name'},
            'state': 'Andhra Pradesh',
            'city': 'Amaravati'
        }
    }

    dfs = []
    for filename, info in files_info.items():
        file_path = os.path.join(data_dir, filename)
        if not os.path.isfile(file_path):
            logging.warning(f"File not found: {file_path}. Skipping.")
            continue

        logging.info(f"Processing {filename}...")
        df = read_and_process_csv(
            file_path,
            rename_map=info['rename_map'],
            state=info.get('state'),
            city=info.get('city')
        )
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
