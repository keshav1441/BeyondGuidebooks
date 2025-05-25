import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster
import random
from A import test_snowflake_connection

# Page configuration
st.set_page_config(
    page_title="Beyond Guide Books",
    page_icon="🏛️",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem !important;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0;
        text-align: center;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #4B5563;
        margin-top: 0;
        margin-bottom: 1rem;
        text-align: center;
    }
    .category-badge {
        display: inline-block;
        padding: 0.25rem 0.5rem;
        border-radius: 9999px;
        font-size: 0.875rem;
        font-weight: 500;
        margin-right: 0.5rem;
        margin-bottom: 0.5rem;
    }
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
    .stButton>button {
        background-color: #4f46e5;
        color: white;
        border-radius: 8px;
        padding: 0.5rem 1rem;
    }
    .stButton>button:hover {
        background-color: #4338ca;
        color: white;
    }
    .site-card {
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        border-left: 4px solid #4f46e5;
    }
    .map-container {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
</style>
""", unsafe_allow_html=True)

# App header
st.markdown('<p class="main-header">Beyond Guide Books</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Discover India\'s rich cultural heritage sites</p>', unsafe_allow_html=True)

# Load data
@st.cache_data(ttl=600)
def load_data():
    try:
        df = test_snowflake_connection()
        

        
        if df.empty:
            st.error("No data received from Snowflake")
            return pd.DataFrame()

        # Clean and standardize - using actual column names
        df = df.dropna(subset=['LATITUDE', 'LONGITUDE'])
        df = df.drop_duplicates(subset=['SITE_NAME', 'CITY'])

        df['LATITUDE'] = pd.to_numeric(df['LATITUDE'], errors='coerce')
        df['LONGITUDE'] = pd.to_numeric(df['LONGITUDE'], errors='coerce')
        df = df.dropna(subset=['LATITUDE', 'LONGITUDE'])

        # Create category based on site name
        df['Category'] = df['SITE_NAME'].apply(lambda x: 'Temple' if 'temple' in str(x).lower()
                                                else 'Fort' if 'fort' in str(x).lower()
                                                else 'Mosque' if 'masjid' in str(x).lower() or 'mosque' in str(x).lower()
                                                else 'Monument')
        
        return df

    except Exception as e:
        st.error(f"Failed to load data from Snowflake: {str(e)}")
        return pd.DataFrame()

df = load_data()

# Check if data is loaded successfully
if df.empty:
    st.error("No data available. Please check your Snowflake connection.")
    st.stop()

# Sidebar filters
with st.sidebar:
    st.header("🔍 Filter Heritage Sites")
    
    # Search by name
    search_term = st.text_input("Search by site name:", "")
    
    # City filter (since we don't have State)
    cities = ["All Cities"] + sorted(df['CITY'].dropna().unique().tolist())
    selected_city = st.selectbox("Select City:", cities)
    
    # Category filter
    categories = ["All Categories"] + sorted(df['Category'].dropna().unique().tolist())
    selected_category = st.selectbox("Select Category:", categories)
    
    st.markdown("---")
    
    # Show data info
    st.markdown(f"**Total Sites:** {len(df)}")

# Apply filters
filtered_df = df.copy()

if search_term:
    filtered_df = filtered_df[filtered_df['SITE_NAME'].str.contains(search_term, case=False, na=False)]

if selected_city != "All Cities":
    filtered_df = filtered_df[filtered_df['CITY'] == selected_city]

if selected_category != "All Categories":
    filtered_df = filtered_df[filtered_df['Category'] == selected_category]

# Main content layout
if not filtered_df.empty:
    # Map and details layout
    col1, col2 = st.columns([7, 3])
    
    with col1:
        st.subheader("📍 Interactive Map")
        with st.spinner("Loading map..."):
            # Create map centered on India
            m = folium.Map(location=[20.5937, 78.9629], zoom_start=5, control_scale=True)
            marker_cluster = MarkerCluster().add_to(m)
            
            # Add markers for each site
            for _, row in filtered_df.iterrows():
                icon_color = {
                    'Temple': 'orange',
                    'Fort': 'blue',
                    'Mosque': 'green',
                    'Monument': 'purple'
                }.get(row['Category'], 'red')
                
                popup_html = f"""
                <div style="width: 250px;">
                    <h4>{row['SITE_NAME']}</h4>
                    <p><b>Location:</b> {row['CITY']}</p>
                    <p><b>Category:</b> {row['Category']}</p>
                </div>
                """
                folium.Marker(
                    location=[row['LATITUDE'], row['LONGITUDE']],
                    popup=folium.Popup(popup_html, max_width=300),
                    icon=folium.Icon(color=icon_color, icon='info-sign'),
                    tooltip=row['SITE_NAME']
                ).add_to(marker_cluster)
            
            # Display the map
            with st.container():
                st_data = st_folium(m, width="100%", height=600)
    
    with col2:
        st.subheader("🏆 Featured Sites")
        st.markdown(f"**Found {len(filtered_df)} sites** matching your criteria")
        
        # Display site cards
        for _, site in filtered_df.iterrows():
            with st.expander(f"{site['SITE_NAME']} ({site['CITY']})", expanded=False):
                st.markdown(f"""
                <div class="site-card">
                    <p><b>Location:</b> {site['CITY']}</p>
                    <p><b>Category:</b> {site['Category']}</p>
                    <p><b>Coordinates:</b> {site['LATITUDE']:.6f}, {site['LONGITUDE']:.6f}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Show directions button
                maps_link = f"https://www.google.com/maps?q={site['LATITUDE']},{site['LONGITUDE']}"
                st.markdown(f"""
                <a href="{maps_link}" target="_blank" style="text-decoration: none;">
                    <button style="
                        background-color: #4f46e5;
                        color: white;
                        border: none;
                        padding: 0.5rem 1rem;
                        border-radius: 8px;
                        cursor: pointer;
                        width: 100%;
                        text-align: center;
                    ">Get Directions</button>
                </a>
                """, unsafe_allow_html=True)
else:
    st.warning("No heritage sites match your current filters. Try adjusting your search criteria.")

# Show some statistics
if not df.empty:
    st.markdown("---")
    st.subheader("📊 Site Statistics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Sites", len(df))
    
    with col2:
        st.metric("Cities", len(df['CITY'].unique()))
    
    with col3:
        temples_count = len(df[df['Category'] == 'Temple'])
        st.metric("Temples", temples_count)
    
    with col4:
        forts_count = len(df[df['Category'] == 'Fort'])
        st.metric("Forts", forts_count)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: #6B7280; font-size: 0.9rem;">
        <p>Created with ❤️ to explore India's cultural heritage</p>
        <p>Data sourced from Snowflake heritage database</p>
    </div>
    """,
    unsafe_allow_html=True
)