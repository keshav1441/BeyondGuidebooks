import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import random

# Load data
df = pd.read_csv("data\\Rajya_Sabha_Session_234_AU2267_4.csv", encoding='windows-1252')

# OPTIONAL: Generate dummy lat/lon for demonstration (replace with actual if available)
if 'Latitude' not in df.columns or 'Longitude' not in df.columns:
    df['Latitude'] = [random.uniform(8.0, 37.0) for _ in range(len(df))]
    df['Longitude'] = [random.uniform(68.0, 97.0) for _ in range(len(df))]

# UI Setup
st.set_page_config(layout="wide")
st.title("🗺️ Interactive Cultural Heritage Map of India")

# Sidebar filters
st.sidebar.header("Filter Cultural Sites")
regions = st.sidebar.multiselect("Select Region/State", options=sorted(df['State'].unique()), default=[])

# Filter data
filtered_df = df.copy()
if regions:
    filtered_df = filtered_df[filtered_df['State'].isin(regions)]

# Map
m = folium.Map(location=[21.1466, 79.0888], zoom_start=5)

for _, row in filtered_df.iterrows():
    popup_html = f"""
    <b>{row['Name of Monument/Site']}</b><br>
    <b>Location:</b> {row['Locality/District']}<br>
    <b>State:</b> {row['State']}<br>
    """

    folium.Marker(
        location=[row['Latitude'], row['Longitude']],
        popup=folium.Popup(popup_html, max_width=300),
        icon=folium.Icon(color="blue")
    ).add_to(m)

# Show map
st_folium(m, width=1200, height=700)
