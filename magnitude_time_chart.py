import json
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.patches as mpatches
from datetime import datetime
import os
import pandas as pd
import numpy as np
import folium
from folium.plugins import MarkerCluster

from constants import MARMARA_BOUNDS, MARMARA_MAP_CENTER, MARMARA_ZOOM_LEVEL
from visualization import is_in_marmara_region, get_magnitude_color, create_map

def get_marmara_earthquakes(earthquake_data):
    """
    Filter earthquakes to include only those in the Marmara region
    based on geographic coordinates.
    """
    marmara_quakes = []
    
    for quake in earthquake_data:
        try:
            lat = float(quake.get('latitude', 0))
            lon = float(quake.get('longitude', 0))
            
            if is_in_marmara_region(lat, lon):
                # Convert date string to datetime object
                date_obj = datetime.fromisoformat(quake['date'].replace('Z', '+00:00'))
                marmara_quakes.append({
                    'date': date_obj,
                    'magnitude': quake['magnitude'],
                    'depth': quake['depth'],
                    'latitude': lat,
                    'longitude': lon,
                    'location': quake['location'],
                    'source': quake['source']
                })
        except (KeyError, ValueError) as e:
            print(f"Error processing earthquake entry: {e}")
            continue
    
    return marmara_quakes

def generate_marmara_map(marmara_quakes, output_file='marmara_earthquakes_map.html'):
    """
    Generate an interactive map showing earthquakes in the Marmara region.
    """
    # Convert to DataFrame
    df = pd.DataFrame(marmara_quakes)
    
    # Create map
    marmara_map = create_map(
        df, 
        center=MARMARA_MAP_CENTER,
        zoom=MARMARA_ZOOM_LEVEL,
        show_marmara_bounds=True
    )
    
    # Save the map
    marmara_map.save(output_file)
    print(f"Marmara region map saved to {output_file}")
    
    # Try to open the HTML file in the default web browser
    try:
        import webbrowser
        webbrowser.open('file://' + os.path.realpath(output_file))
    except:
        pass
    
    return True

def generate_magnitude_time_chart(json_file='combined_earthquakes.json', output_file='marmara_magnitude_time.png', map_output_file='marmara_earthquakes_map.html'):
    """
    Generates a chart showing earthquake magnitudes over time for the Marmara region,
    and a map visualization of the earthquakes.
    
    Args:
        json_file: Path to the JSON file containing earthquake data
        output_file: Path to save the output chart image
        map_output_file: Path to save the output map HTML file
    """
    # Load earthquake data from JSON file
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            earthquake_data = json.load(f)
    except Exception as e:
        print(f"Error loading earthquake data: {e}")
        return False
    
    # Filter for Marmara region earthquakes based on coordinates
    marmara_quakes = get_marmara_earthquakes(earthquake_data)
    
    if not marmara_quakes:
        print("No earthquakes found for Marmara region")
        return False
    
    print(f"Found {len(marmara_quakes)} earthquakes in the Marmara region.")
    
    # Generate map visualization
    generate_marmara_map(marmara_quakes, map_output_file)
    
    # Convert to DataFrame for easier manipulation
    df = pd.DataFrame(marmara_quakes)
    
    # Sort by date
    df = df.sort_values('date')
    
    # Create figure and axis for matplotlib chart
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Define magnitude ranges and colors
    ranges = [
        {'min': 0, 'max': 2.0, 'color': '#91cf60', 'label': '< 2.0'},
        {'min': 2.0, 'max': 3.0, 'color': '#d9ef8b', 'label': '2.0 - 2.9'},
        {'min': 3.0, 'max': 4.0, 'color': '#fee08b', 'label': '3.0 - 3.9'},
        {'min': 4.0, 'max': 5.0, 'color': '#fc8d59', 'label': '4.0 - 4.9'},
        {'min': 5.0, 'max': 10.0, 'color': '#d73027', 'label': '≥ 5.0'}
    ]
    
    # Plot earthquakes by magnitude range
    patches = []
    for r in ranges:
        mask = (df['magnitude'] >= r['min']) & (df['magnitude'] < r['max'])
        if any(mask):
            ax.scatter(df.loc[mask, 'date'], df.loc[mask, 'magnitude'], 
                      c=r['color'], alpha=0.7, edgecolors='k', s=30 + 10 * df.loc[mask, 'magnitude'],
                      label=r['label'])
            patches.append(mpatches.Patch(color=r['color'], label=r['label']))
    
    # Configure the chart
    ax.set_title('Marmara Bölgesi Deprem Büyüklükleri (Zaman Grafiği)', fontsize=14)
    ax.set_xlabel('Tarih', fontsize=12)
    ax.set_ylabel('Büyüklük (M)', fontsize=12)
    ax.grid(True, linestyle='--', alpha=0.7)
    ax.set_ylim(bottom=0)
    
    # Format x-axis dates
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    fig.autofmt_xdate()
    
    # Add legend
    ax.legend(handles=patches, title='Büyüklük (M)', loc='upper left')
    
    # Add a horizontal line at magnitude 4.0
    ax.axhline(y=4.0, color='r', linestyle='--', alpha=0.5)
    ax.text(df['date'].iloc[0], 4.1, 'M4.0', color='r', alpha=0.7)
    
    # Save the figure
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Magnitude-time chart saved to {output_file}")
    
    # Try to open the image file
    try:
        from PIL import Image
        img = Image.open(output_file)
        img.show()
    except:
        pass
    
    plt.close()
    
    return True

if __name__ == "__main__":
    # Generate chart from sample data if available
    json_file = 'combined_earthquakes.json'
    if os.path.exists(json_file):
        generate_magnitude_time_chart(json_file)
    else:
        print(f"File {json_file} not found. Please run the data collection first.") 