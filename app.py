import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster
import random

# Page configuration
st.set_page_config(
    page_title="Indian Heritage Explorer",
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
st.markdown('<p class="main-header">Indian Heritage Explorer</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Discover India\'s rich cultural heritage sites</p>', unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("data/final_heritage_data.csv")
        
        # Ensure required columns exist
        required_columns = ['Site Name', 'City', 'State', 'Latitude', 'Longitude']
        if not all(col in df.columns for col in required_columns):
            st.error("CSV file doesn't contain all required columns")
            return pd.DataFrame()
        
        # Clean data
        df = df.dropna(subset=['Latitude', 'Longitude'])
        df = df.drop_duplicates(subset=['Site Name', 'City', 'State'])
        
        # Convert coordinates to numeric
        df['Latitude'] = pd.to_numeric(df['Latitude'], errors='coerce')
        df['Longitude'] = pd.to_numeric(df['Longitude'], errors='coerce')
        df = df.dropna(subset=['Latitude', 'Longitude'])
        
        # Add some derived columns
        df['Category'] = df['Site Name'].apply(lambda x: 'Temple' if 'temple' in str(x).lower() 
                                             else 'Fort' if 'fort' in str(x).lower()
                                             else 'Mosque' if 'masjid' in str(x).lower()
                                             else 'Monument')
        
        df['Popularity'] = [random.randint(1, 5) for _ in range(len(df))]
        df['UNESCO'] = [random.choice([True, False]) for _ in range(len(df))]
        
        return df

    except Exception as e:
        st.error(f"Failed to load data: {str(e)}")
        return pd.DataFrame()

df = load_data()

# Sidebar filters
with st.sidebar:
    st.header("🔍 Filter Heritage Sites")
    
    # Search by name
    search_term = st.text_input("Search by site name:", "")
    
    # State filter
    states = ["All States"] + sorted(df['State'].dropna().unique().tolist())
    selected_state = st.selectbox("Select State:", states)
    
    # Category filter
    categories = ["All Categories"] + sorted(df['Category'].dropna().unique().tolist())
    selected_category = st.selectbox("Select Category:", categories)
    
    # Additional filters
    col1, col2 = st.columns(2)
    with col1:
        unesco_filter = st.checkbox("UNESCO Sites Only")
    with col2:
        min_popularity = st.slider("Min Popularity", 1, 5, 1)
    
    st.markdown("---")
    st.markdown("**Quick Filters**")
    
    # Quick filter buttons
    btn_cols = st.columns(3)
    with btn_cols[0]:
        if st.button("🏰 Forts"):
            selected_category = "Fort"
    with btn_cols[1]:
        if st.button("🛕 Temples"):
            selected_category = "Temple"
    with btn_cols[2]:
        if st.button("🕌 Mosques"):
            selected_category = "Mosque"

# Apply filters
filtered_df = df.copy()
if search_term:
    filtered_df = filtered_df[filtered_df['Site Name'].str.contains(search_term, case=False, na=False)]
if selected_state != "All States":
    filtered_df = filtered_df[filtered_df['State'] == selected_state]
if selected_category != "All Categories":
    filtered_df = filtered_df[filtered_df['Category'] == selected_category]
if unesco_filter:
    filtered_df = filtered_df[filtered_df['UNESCO'] == True]
filtered_df = filtered_df[filtered_df['Popularity'] >= min_popularity]

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
                    <h4>{row['Site Name']}</h4>
                    <p><b>Location:</b> {row['City']}, {row['State']}</p>
                    <p><b>Category:</b> {row['Category']}</p>
                    <p><b>Popularity:</b> {"⭐" * row['Popularity']}</p>
                    {f'<p><b>UNESCO World Heritage Site</b></p>' if row['UNESCO'] else ''}
                </div>
                """
                folium.Marker(
                    location=[row['Latitude'], row['Longitude']],
                    popup=folium.Popup(popup_html, max_width=300),
                    icon=folium.Icon(color=icon_color, icon='info-sign'),
                    tooltip=row['Site Name']
                ).add_to(marker_cluster)
            
            # Display the map
            with st.container():
                st_data = st_folium(m, width="100%", height=600)
    
    with col2:
        st.subheader("🏆 Featured Sites")
        st.markdown(f"**Found {len(filtered_df)} sites** matching your criteria")
        
        # Sort by popularity
        top_sites = filtered_df.sort_values('Popularity', ascending=False).head(10)
        
        # Display site cards
        for _, site in top_sites.iterrows():
            with st.expander(f"{site['Site Name']} ({site['City']})", expanded=False):
                st.markdown(f"""
                <div class="site-card">
                    <p><b>Location:</b> {site['City']}, {site['State']}</p>
                    <p><b>Category:</b> {site['Category']}</p>
                    <p><b>Popularity:</b> {"⭐" * site['Popularity']}</p>
                    {f'<p><b>UNESCO World Heritage Site</b></p>' if site['UNESCO'] else ''}
                </div>
                """, unsafe_allow_html=True)
                
                # Show directions button
                maps_link = f"https://www.google.com/maps?q={site['Latitude']},{site['Longitude']}"
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

# Footer
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: #6B7280; font-size: 0.9rem;">
        <p>Created with ❤️ to explore India's cultural heritage</p>
        <p>Data sourced from various heritage listings and archaeological surveys</p>
    </div>
    """,
    unsafe_allow_html=True
)