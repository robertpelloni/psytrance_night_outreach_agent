import folium
import json
from src.analytics import AnalyticsEngine
from src.db_manager import DatabaseManager

analytics = AnalyticsEngine(db_path='database/outreach.db')
db = DatabaseManager(db_path='database/outreach.db')

# Ensure we have the Detroit anchor venue (from seed or create one)
db.add_venue({'id': 'detroit_anchor', 'name': 'Detroit Anchor (HQ)', 'city': 'Detroit', 'latitude': 42.3314, 'longitude': -83.0458})
db.add_lead({'venue_id': 'detroit_anchor', 'vibe_score': 10, 'pipeline_status': 'APPROVED'})

clusters = analytics.get_venue_clusters()

m = folium.Map(location=[42.3314, -83.0458], zoom_start=8) # Detroit coords

# Add Detroit Anchor manually if it's not clustered properly due to radius
folium.Marker(
    location=[42.3314, -83.0458],
    popup="Detroit Anchor (HQ)",
    icon=folium.Icon(color='red', icon='star')
).add_to(m)

colors = ['blue', 'green', 'purple', 'orange', 'darkred', 'lightred', 'beige', 'darkblue', 'darkgreen']

all_points = [[42.3314, -83.0458]] # Start route at Detroit anchor

for idx, cluster in enumerate(clusters):
    color = colors[idx % len(colors)]

    # Add marker for the cluster center
    folium.Marker(
        location=[cluster['center']['lat'], cluster['center']['lon']],
        popup=f"Cluster {idx+1} Center (Avg Vibe: {cluster['avg_vibe']:.1f})",
        icon=folium.Icon(color=color, icon='info-sign')
    ).add_to(m)

    venues = cluster['venues']

    # Simple sort by longitude to create a basic linear route
    venues_sorted = sorted(venues, key=lambda v: v['longitude'])

    for venue in venues_sorted:
        if venue['vibe_score'] >= 6: # Only map high vibe score venues in the route
            all_points.append([venue['latitude'], venue['longitude']])
            folium.CircleMarker(
                location=[venue['latitude'], venue['longitude']],
                radius=6,
                popup=f"{venue['name']} (Vibe: {venue['vibe_score']})",
                color=color,
                fill=True,
                fill_color=color
            ).add_to(m)
        else:
            folium.CircleMarker(
                location=[venue['latitude'], venue['longitude']],
                radius=3,
                popup=f"{venue['name']} (Vibe: {venue['vibe_score']})",
                color='gray',
                fill=True,
                fill_color='gray'
            ).add_to(m)

# Draw master route connecting the anchor to the high vibe spots
if len(all_points) > 1:
    folium.PolyLine(all_points, color='black', weight=2.5, opacity=0.8, dash_array='5, 5').add_to(m)

m.save('midwest_circuit_map.html')
print(f"Map generated and saved to midwest_circuit_map.html with {len(clusters)} clusters and route connected to Detroit anchor.")
