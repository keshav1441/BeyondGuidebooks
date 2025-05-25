import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster
import random
import snowflake.connector
import pandas as pd
import os
from dotenv import load_dotenv
load_dotenv()

def test_snowflake_connection():
    conn = snowflake.connector.connect(
        user=st.secrets["SNOWFLAKE_USER"],
        password=st.secrets["SNOWFLAKE_PASSWORD"],
        account=st.secrets["SNOWFLAKE_ACCOUNT"],
        warehouse=st.secrets["SNOWFLAKE_WAREHOUSE"],
        database=st.secrets["SNOWFLAKE_DATABASE"],
        schema=st.secrets["SNOWFLAKE_SCHEMA"]
    )
    try:
        cursor = conn.cursor()
        query = "SELECT * FROM SITES"
        cursor.execute(query)

        # Fetch all data
        data = cursor.fetchall()

        # Get column names
        columns = [desc[0] for desc in cursor.description]

        # Convert to DataFrame for easy viewing
        df = pd.DataFrame(data, columns=columns)

        print("Data from Snowflake SITES table:")
        print(df)
        
        return df

    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    df = test_snowflake_connection()
    print(df)


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
        padding: 0.5rem !important;
        margin-bottom: 0.5rem !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        border-left: 4px solid #4f46e5;
    }
    .map-container {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    
    /* CRITICAL SPACING FIXES */
    .main .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
        max-width: 100% !important;
    }
    
    /* Remove extra spacing between elements */
    .element-container {
        margin-bottom: 0.25rem !important;
    }
    
    /* Compact columns */
    div[data-testid="column"] {
        padding: 0 0.25rem !important;
        gap: 0.5rem !important;
    }
    
    /* Compact expanders */
    .streamlit-expanderHeader {
        padding: 0.25rem 0.5rem !important;
        margin-bottom: 0.1rem !important;
    }
    
    .streamlit-expanderContent {
        padding: 0.5rem !important;
    }
    
    /* Remove extra space around metrics */
    div[data-testid="metric-container"] {
        margin-bottom: 0.25rem !important;
        padding: 0.25rem !important;
    }
    
    /* Compact the right column */
    .sites-list {
        max-height: 580px !important;
        overflow-y: auto !important;
        padding-right: 5px !important;
    }
    
    /* Remove space after map */
    iframe[title="streamlit_folium.st_folium"] {
        margin-bottom: 0 !important;
    }
    
    /* Compact headings */
    .stMarkdown h3 {
        margin-top: 0.5rem !important;
        margin-bottom: 0.25rem !important;
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
    states = ["All States"] + sorted(df['STATE'].dropna().unique().tolist())
    selected_city = st.selectbox("Select States:", states)
    
    # Category filter
    categories = ["All Categories"] + sorted(df['Category'].dropna().unique().tolist())
    selected_category = st.selectbox("Select Category:", categories)
    
    st.markdown("---")
    
    # Move statistics to sidebar to save space
    st.markdown("**📊 Quick Stats**")
    st.markdown(f"**Total Sites:** {len(df)}")
    st.markdown(f"**Cities:** {len(df['CITY'].unique())}")
    temples_count = len(df[df['Category'] == 'Temple'])
    st.markdown(f"**Temples:** {temples_count}")
    forts_count = len(df[df['Category'] == 'Fort'])
    st.markdown(f"**Forts:** {forts_count}")

# Apply filters
filtered_df = df.copy()

if search_term:
    filtered_df = filtered_df[filtered_df['SITE_NAME'].str.contains(search_term, case=False, na=False)]

if selected_city != "All States":
    filtered_df = filtered_df[filtered_df['STATE'] == selected_city]

if selected_category != "All Categories":
    filtered_df = filtered_df[filtered_df['Category'] == selected_category]

# Main content layout
if not filtered_df.empty:
    # Map and details layout - adjusted column ratio for better balance
    col1, col2 = st.columns([8, 2])
    
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
                
                # Create directions link
                maps_link = f"https://www.google.com/maps?q={row['LATITUDE']},{row['LONGITUDE']}"
                
                popup_html = f"""
                <div style="width: 250px;">
                    <h4>{row['SITE_NAME']}</h4>
                    <p><b>Location:</b> {row['CITY']}</p>
                    <p><b>Category:</b> {row['Category']}</p>
                    <p style="margin:0.2rem 0; font-size:0.8rem;"><b>Co-ordinates:</b> {row['LATITUDE']:.4f}, {row['LONGITUDE']:.4f}</p>
                    <a href="{maps_link}" target="_blank" style="text-decoration: none;">
                        <button style="
                            background-color: #4f46e5;
                            color: white;
                            border: none;
                            padding: 0.3rem 0.6rem;
                            border-radius: 6px;
                            cursor: pointer;
                            width: 100%;
                            text-align: center;
                            font-size: 0.85rem;
                            margin-top: 0.5rem;
                        ">📍 Get Directions</button>
                    </a>
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
        st.subheader("🏆 Top 5 Sites")
        total_sites = len(filtered_df)
        showing_count = min(5, total_sites)
        st.markdown(f"**Showing {showing_count} of {total_sites} sites**")
        
        # Create scrollable container for site list
        st.markdown('<div class="sites-list">', unsafe_allow_html=True)
        
        # Display only top 5 site cards
        for _, site in filtered_df.head(5).iterrows():
            with st.expander(f"{site['SITE_NAME'][:25]}{'...' if len(site['SITE_NAME']) > 25 else ''}", expanded=False):
                st.markdown(f"""
                <div class="site-card">
                    <p style="margin:0.2rem 0;"><b>City:</b> {site['CITY']}</p>
                    <p style="margin:0.2rem 0;"><b>Type:</b> {site['Category']}</p>
                    <p style="margin:0.2rem 0; font-size:0.8rem;"><b>Coords:</b> {site['LATITUDE']:.4f}, {site['LONGITUDE']:.4f}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Compact directions button
                maps_link = f"https://www.google.com/maps?q={site['LATITUDE']},{site['LONGITUDE']}"
                st.markdown(f"""
                <a href="{maps_link}" target="_blank" style="text-decoration: none;">
                    <button style="
                        background-color: #4f46e5;
                        color: white;
                        border: none;
                        padding: 0.3rem 0.6rem;
                        border-radius: 6px;
                        cursor: pointer;
                        width: 100%;
                        text-align: center;
                        font-size: 0.85rem;
                    ">📍 Get Directions</button>
                </a>
                """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Show note if there are more sites
        if total_sites > 5:
            st.markdown(f"<small style='color: #6B7280;'>📍 {total_sites - 5} more sites available on map</small>", unsafe_allow_html=True)

else:
    st.warning("No heritage sites match your current filters. Try adjusting your search criteria.")

# Footer - more compact
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: #6B7280; font-size: 0.8rem; padding: 0.5rem;">
        <p style="margin:0;">Created with ❤️ to explore India's cultural heritage • Data from Snowflake</p>
    </div>
    """,
    unsafe_allow_html=True
)