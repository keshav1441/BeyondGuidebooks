import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster
import random

# Page configuration
st.set_page_config(
    page_title="Discover India - Interactive Tourist Map",
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
    }
    .sub-header {
        font-size: 1.5rem;
        color: #4B5563;
        margin-top: 0;
        margin-bottom: 1rem;
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
    .category-badge.temple { background-color: #FEF3C7; color: #92400E; }
    .category-badge.fort { background-color: #DBEAFE; color: #1E3A8A; }
    .category-badge.palace { background-color: #F3E8FF; color: #6B21A8; }
    .category-badge.monument { background-color: #DCFCE7; color: #166534; }
    .category-badge.tomb { background-color: #E5E7EB; color: #374151; }
    .category-badge.unesco { background-color: #FEE2E2; color: #B91C1C; }
</style>
""", unsafe_allow_html=True)

# App header
st.markdown('<p class="main-header">Discover India</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Explore India\'s rich cultural heritage and tourist destinations</p>', unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("data/final_heritage_data.csv", header=0)
        
        df = df.rename(columns={
            'Site Name': 'Name of Monument/Site',
            'City': 'Locality/District',
            'State': 'Region'
        })
        
        df['Latitude'] = pd.to_numeric(df['Latitude'], errors='coerce')
        df['Longitude'] = pd.to_numeric(df['Longitude'], errors='coerce')
        df = df.dropna(subset=['Latitude', 'Longitude'])

        def categorize_site(name):
            name = name.lower()
            if 'temple' in name or 'mandir' in name:
                return 'Temple'
            elif 'fort' in name or 'qila' in name:
                return 'Fort'
            elif 'palace' in name or 'mahal' in name:
                return 'Palace'
            elif 'tomb' in name or 'mausoleum' in name:
                return 'Tomb'
            else:
                return 'Monument'

        df['Category'] = df['Name of Monument/Site'].apply(categorize_site)
        df['UNESCO'] = [random.choice([True, False]) for _ in range(len(df))]
        df['Popularity'] = [random.randint(1, 5) for _ in range(len(df))]
        return df

    except Exception as e:
        st.error(f"Failed to load data: {e}")
        return pd.DataFrame()

df = load_data()
print(df.head())  # Debugging line to check the data

# Sidebar filters
with st.sidebar:
    st.header("🔍 Find Your Perfect Destination")
    search_term = st.text_input("Search by name:", "")
    states = ["All States"] + sorted(df['Region'].dropna().unique().tolist())
    selected_state = st.selectbox("Select Region:", states)
    categories = ["All Categories"] + sorted(df['Category'].dropna().unique().tolist())
    selected_category = st.selectbox("Monument Type:", categories)
    unesco_filter = st.checkbox("UNESCO World Heritage Sites Only")
    min_popularity = st.slider("Minimum Popularity:", 1, 5, 1)

# Apply filters
filtered_df = df.copy()
if search_term:
    filtered_df = filtered_df[filtered_df['Name of Monument/Site'].str.contains(search_term, case=False)]
if selected_state != "All States":
    filtered_df = filtered_df[filtered_df['Region'] == selected_state]
if selected_category != "All Categories":
    filtered_df = filtered_df[filtered_df['Category'] == selected_category]
if unesco_filter:
    filtered_df = filtered_df[filtered_df['UNESCO'] == True]
filtered_df = filtered_df[filtered_df['Popularity'] >= min_popularity]

# Map and details layout
col1, col2 = st.columns([7, 3])

with col1:
    m = folium.Map(location=[22.9734, 78.6569], zoom_start=5)
    marker_cluster = MarkerCluster().add_to(m)

    for _, row in filtered_df.iterrows():
        icon_color = {
            'Temple': 'orange',
            'Fort': 'blue',
            'Palace': 'purple',
            'Tomb': 'gray',
            'Monument': 'green'
        }.get(row['Category'], 'blue')

        popup_html = f"""
        <div style="width: 250px;">
            <h4>{row['Name of Monument/Site']}</h4>
            <p><b>Location:</b> {row['Locality/District']}, {row['State']}</p>
            <p><b>Category:</b> {row['Category']}</p>
            <p><b>Popularity:</b> {"⭐" * row['Popularity']}</p>
            {f'<p><b>UNESCO World Heritage Site</b></p>' if row['UNESCO'] else ''}
        </div>
        """
        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            popup=folium.Popup(popup_html, max_width=300),
            icon=folium.Icon(color=icon_color),
            tooltip=row['Name of Monument/Site']
        ).add_to(marker_cluster)

    st_data = st_folium(m, width="100%", height=600)

with col2:
    st.subheader("🏛️ Featured Destinations")
    if not filtered_df.empty:
        st.markdown(f"**Found {len(filtered_df)} destinations** matching your criteria")
        top_sites = filtered_df.sort_values('Popularity', ascending=False).head(5)

        for _, site in top_sites.iterrows():
            with st.expander(site['Name of Monument/Site']):
                st.markdown(f"**Location:** {site['Locality/District']}, {site['State']}")
                badge_class = site['Category'].lower()
                st.markdown(f"""
                <span class="category-badge {badge_class}">{site['Category']}</span>
                {'<span class="category-badge unesco">UNESCO World Heritage</span>' if site['UNESCO'] else ''}
                """, unsafe_allow_html=True)
                st.markdown(f"**Popularity:** {'⭐' * site['Popularity']}")
    else:
        st.info("No destinations match your current filters. Try adjusting your search.")

# Footer
st.markdown("---")
st.markdown(
    "Created with ❤️ to explore India's cultural landmarks. "
    "Data sourced from ASI and custom-scraped heritage listings."
)