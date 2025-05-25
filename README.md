# BeyondGuidebooks

A Python application for managing and analyzing heritage site data across different regions of India, developed for the Snowflake Hackathon.

## Overview

This project processes and merges heritage site data from various sources, creating a standardized dataset with geocoding information. It helps in organizing and visualizing cultural heritage sites, monuments, and historical places.

## Features

- Merges heritage data from multiple CSV sources
- Standardizes data format across different sources
- Includes geocoding for heritage sites
- Provides unified access to heritage information
- Supports data from multiple regions (Delhi, Ahmedabad, Karnataka, etc.)

## Requirements

- Python 3.x
- Required packages (install via pip):
  ```
  streamlit
  pandas
  folium
  streamlit-folium
  geopandas
  geopy
  ```

## Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Data Processing

To merge heritage data files:

```bash
python merge_heritage_data.py
```

This will:

- Process all CSV files in the data directory
- Standardize column names
- Create a merged dataset with geocoding information
- Save the result as 'merged_heritage_data.csv'

### Web Application

To run the Streamlit web application:

```bash
streamlit run app.py
```

## Output Format

The merged data includes the following columns:

- name: Name of the heritage site/monument
- city: City where the site is located
- state: State where the site is located
- address: Complete address of the site
- latitude: Geocoded latitude
- longitude: Geocoded longitude
