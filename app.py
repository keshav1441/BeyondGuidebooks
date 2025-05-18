import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster
import random
import base64

# Page configuration
st.set_page_config(
    page_title="Discover India - Interactive Tourist Map",
    page_icon="🏛️",
    layout="wide"
)

# Custom CSS for better styling
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
    .info-card {
        background-color: #F3F4F6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .highlight {
        background-color: #DBEAFE;
        padding: 0.2rem 0.5rem;
        border-radius: 0.2rem;
        font-weight: 500;
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
    .category-badge.temple {
        background-color: #FEF3C7;
        color: #92400E;
    }
    .category-badge.fort {
        background-color: #DBEAFE;
        color: #1E3A8A;
    }
    .category-badge.palace {
        background-color: #F3E8FF;
        color: #6B21A8;
    }
    .category-badge.monument {
        background-color: #DCFCE7;
        color: #166534;
    }
    .category-badge.unesco {
        background-color: #FEE2E2;
        color: #B91C1C;
    }
</style>
""", unsafe_allow_html=True)

# App title and description
st.markdown('<p class="main-header">Discover India</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Explore India\'s rich cultural heritage and tourist destinations</p>', unsafe_allow_html=True)


# Function to load data
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("data\\Rajya_Sabha_Session_234_AU2267_4.csv", encoding='windows-1252')
        
        # Add missing columns if needed
        if 'Latitude' not in df.columns or 'Longitude' not in df.columns:
            df['Latitude'] = [random.uniform(8.0, 37.0) for _ in range(len(df))]
            df['Longitude'] = [random.uniform(68.0, 97.0) for _ in range(len(df))]
        
        # Add category classification based on name keywords
        def categorize_site(name):
            name_lower = name.lower()
            if 'temple' in name_lower or 'mandir' in name_lower:
                return 'Temple'
            elif 'fort' in name_lower or 'qila' in name_lower:
                return 'Fort'
            elif 'palace' in name_lower or 'mahal' in name_lower:
                return 'Palace'
            elif 'tomb' in name_lower or 'mausoleum' in name_lower:
                return 'Tomb'
            else:
                return 'Monument'
        
        df['Category'] = df['Name of Monument/Site'].apply(categorize_site)
        
        # Add dummy UNESCO status (replace with actual data if available)
        df['UNESCO'] = [random.choice([True, False]) for _ in range(len(df))]
        
        # Add popularity score (replace with actual data if available)
        df['Popularity'] = [random.randint(1, 5) for _ in range(len(df))]
        
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        # Create sample data if file not found
        return create_sample_data()

def create_sample_data():
    # Create sample data with major Indian tourist sites
    data = {
        'Name of Monument/Site': [
            'Taj Mahal', 'Red Fort', 'Qutub Minar', 'Ajanta Caves', 
            'Ellora Caves', 'Khajuraho Temples', 'Humayun\'s Tomb',
            'Golden Temple', 'Mysore Palace', 'Mahabodhi Temple',
            'Konark Sun Temple', 'Hawa Mahal', 'Gateway of India',
            'Victoria Memorial', 'Hampi Ruins', 'Fatehpur Sikri'
        ],
        'Locality/District': [
            'Agra', 'Delhi', 'Delhi', 'Aurangabad', 
            'Aurangabad', 'Chhatarpur', 'Delhi',
            'Amritsar', 'Mysore', 'Gaya',
            'Puri', 'Jaipur', 'Mumbai',
            'Kolkata', 'Bellary', 'Agra'
        ],
        'State': [
            'Uttar Pradesh', 'Delhi', 'Delhi', 'Maharashtra', 
            'Maharashtra', 'Madhya Pradesh', 'Delhi',
            'Punjab', 'Karnataka', 'Bihar',
            'Odisha', 'Rajasthan', 'Maharashtra',
            'West Bengal', 'Karnataka', 'Uttar Pradesh'
        ],
        'Latitude': [
            27.1751, 28.6562, 28.5245, 20.5522,
            20.0258, 24.8318, 28.5933,
            31.6200, 12.3052, 24.6961,
            19.8876, 26.9239, 18.9220,
            22.5448, 15.3350, 27.0940
        ],
        'Longitude': [
            78.0421, 77.2410, 77.1855, 75.7030,
            75.1780, 79.9199, 77.2507,
            74.8766, 76.6552, 84.9911,
            86.0945, 75.8267, 72.8347,
            88.3426, 76.4600, 77.6701
        ]
    }
    
    df = pd.DataFrame(data)
    
    # Add category classification
    def categorize_site(name):
        name_lower = name.lower()
        if 'temple' in name_lower or 'mandir' in name_lower:
            return 'Temple'
        elif 'fort' in name_lower or 'qila' in name_lower:
            return 'Fort'
        elif 'palace' in name_lower or 'mahal' in name_lower:
            return 'Palace'
        elif 'tomb' in name_lower or 'mausoleum' in name_lower:
            return 'Tomb'
        else:
            return 'Monument'
    
    df['Category'] = df['Name of Monument/Site'].apply(categorize_site)
    
    # Add UNESCO status
    df['UNESCO'] = [True, True, True, True, True, True, True, False, False, True, True, False, False, False, True, True]
    
    # Add popularity score
    df['Popularity'] = [5, 4, 4, 3, 3, 4, 3, 5, 4, 3, 4, 3, 4, 3, 4, 3]
    
    return df

# Load data
df = load_data()

# Sidebar filters
with st.sidebar:
    st.header("🔍 Find Your Perfect Destination")
    
    # Search by name
    search_term = st.text_input("Search by name:", "")
    
    # Filter by state
    states = ["All States"] + sorted(df['State'].unique().tolist())
    selected_state = st.selectbox("Select State/UT:", states)
    
    # Filter by category
    categories = ["All Categories"] + sorted(df['Category'].unique().tolist())
    selected_category = st.selectbox("Monument Type:", categories)
    
    # UNESCO filter
    unesco_filter = st.checkbox("UNESCO World Heritage Sites Only")
    
    # Popularity filter
    min_popularity = st.slider("Minimum Popularity:", 1, 5, 1)
    
    # Apply filters
    st.sidebar.markdown("---")
    st.sidebar.markdown("### About This App")
    st.sidebar.info(
        "Discover India's cultural treasures with our interactive map. "
        "Explore ancient temples, majestic forts, and historical monuments "
        "across the country."
    )

# Apply filters
filtered_df = df.copy()

if search_term:
    filtered_df = filtered_df[filtered_df['Name of Monument/Site'].str.contains(search_term, case=False)]

if selected_state != "All States":
    filtered_df = filtered_df[filtered_df['State'] == selected_state]

if selected_category != "All Categories":
    filtered_df = filtered_df[filtered_df['Category'] == selected_category]

if unesco_filter:
    filtered_df = filtered_df[filtered_df['UNESCO'] == True]

filtered_df = filtered_df[filtered_df['Popularity'] >= min_popularity]

# Create two columns for layout
col1, col2 = st.columns([7, 3])

with col1:
    # Create the base map
    m = folium.Map(location=[22.5937, 78.9629], zoom_start=5, tiles="OpenStreetMap")
    
    # Create marker cluster
    marker_cluster = MarkerCluster().add_to(m)
    
    # Add markers to the map
    for _, row in filtered_df.iterrows():
        # Determine icon color based on category
        icon_color = {
            'Temple': 'orange',
            'Fort': 'blue',
            'Palace': 'purple',
            'Tomb': 'gray',
            'Monument': 'green'
        }.get(row['Category'], 'blue')
        
        # Create popup content
        popup_html = f"""
        <div style="width: 250px;">
            <h3>{row['Name of Monument/Site']}</h3>
            <p><b>Location:</b> {row['Locality/District']}, {row['State']}</p>
            <p><b>Category:</b> {row['Category']}</p>
            <p><b>Popularity:</b> {"⭐" * row['Popularity']}</p>
            {f'<p><b>UNESCO World Heritage Site</b></p>' if row['UNESCO'] else ''}
            <p><a href="#" onclick="parent.postMessage({{'name': '{row['Name of Monument/Site']}', 'lat': {row['Latitude']}, 'lon': {row['Longitude']}}}, '*')">View Details</a></p>
        </div>
        """
        
        # Add marker
        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            popup=folium.Popup(popup_html, max_width=300),
            icon=folium.Icon(color=icon_color, icon="info-sign" if row['UNESCO'] else None),
            tooltip=row['Name of Monument/Site']
        ).add_to(marker_cluster)
    
    # Display the map
    st_data = st_folium(m, width="100%", height=600)

with col2:
    st.subheader("🏛️ Featured Destinations")
    
    if len(filtered_df) > 0:
        # Display counts 
        total_count = len(filtered_df)
        st.markdown(f"**Found {total_count} destinations** matching your criteria")
        
        # Display top 5 popular destinations
        top_sites = filtered_df.sort_values('Popularity', ascending=False).head(5)
        
        for _, site in top_sites.iterrows():
            with st.expander(f"{site['Name of Monument/Site']}"):
                st.markdown(f"**Location:** {site['Locality/District']}, {site['State']}")
                
                # Category badges
                category_class = site['Category'].lower() if site['Category'].lower() in ['temple', 'fort', 'palace', 'monument'] else 'monument'
                st.markdown(f"""
                <span class="category-badge {category_class}">{site['Category']}</span>
                {f'<span class="category-badge unesco">UNESCO World Heritage</span>' if site['UNESCO'] else ''}
                """, unsafe_allow_html=True)
                
                st.markdown(f"**Popularity:** {'⭐' * site['Popularity']}")
                
                # Random description (in a real app, this would come from your database)
                descriptions = [
                    "A magnificent example of architectural brilliance that attracts visitors from around the world.",
                    "This historical site showcases India's rich cultural heritage and artistic tradition.",
                    "An iconic landmark that has stood the test of time, representing a glorious chapter in India's history.",
                    "A popular tourist destination known for its stunning architecture and historical significance.",
                    "This cultural marvel showcases exquisite craftsmanship and is a testimony to India's rich past."
                ]
                st.write(random.choice(descriptions))
                
                st.button(f"Show on map", key=f"btn_{site['Name of Monument/Site']}")
    else:
        st.info("No destinations match your current filters. Please try adjusting your search criteria.")
    
    # Travel tips section
    with st.expander("📝 Travel Tips"):
        st.markdown("""
        - **Best time to visit:** October to March is generally the best time to visit most parts of India
        - **Transportation:** Consider hiring a local guide for historic monuments
        - **Photography:** Early morning visits offer the best lighting for photography
        - **Tickets:** Many popular sites offer online booking to avoid queues
        - **Local customs:** Research local customs and dress codes before visiting religious sites
        """)

# Footer
st.markdown("---")
st.markdown(
    "Created with ❤️ for travelers exploring India's cultural heritage. "
    "Data sourced from Archaeological Survey of India and other public records."
)