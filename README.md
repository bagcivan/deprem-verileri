# Earthquake Data Collection and Combination

This project collects, processes, and visualizes earthquake data from Turkish earthquake monitoring services:
1. Kandilli Observatory (KOERI) - Boğaziçi University
2. AFAD (Disaster and Emergency Management Authority)

It offers both command-line tools and an interactive Streamlit web application for data visualization and analysis.

## Project Structure

The project is organized into modular components:

- `main.py`: Command-line script that coordinates data fetching, combination, and saving
- `streamlit_app.py`: Interactive web application for visualizing earthquake data
- `kandilli.py`: Module for fetching and parsing Kandilli Observatory data
- `afad.py`: Module for fetching and parsing AFAD data (converts UTC to Turkey local time UTC+3)
- `utils.py`: Utility functions for deduplication and file saving
- `map_visualization.py`: Creates an interactive HTML map with Leaflet.js
- `magnitude_time_chart.py`: Generates magnitude-time distribution charts for the Marmara region

## Requirements

Install the required packages:

```bash
pip install -r requirements.txt
```

## Interactive Web Application (Streamlit)

The easiest way to use this project is through the Streamlit web application:

```bash
streamlit run streamlit_app.py
```

The interactive application provides:

- Real-time data fetching from both Kandilli and AFAD APIs
- Interactive maps with earthquake locations
- Magnitude-time distribution charts
- Statistical analysis and visualizations
- Multiple filtering options (magnitude, region, time period)
- Data download in various formats (CSV, Excel, JSON)

![Streamlit App](https://example.com/app_screenshot.png)

## Command-Line Usage

For scripting or automation, you can also use the command-line interface:

```bash
python main.py [options]
```

Command-line options:
- `--save-xlsx`: Also save data to Excel XLSX format
- `--no-map`: Skip generating the map visualization
- `--hours N`: Number of hours of AFAD data to fetch (default: 48)
- `--marmara-chart`: Generate magnitude-time chart for Marmara region earthquakes
- `--only-marmara-chart`: Only generate the Marmara chart (skips map generation)

Examples:
```bash
# Basic usage - saves JSON and generates map
python main.py

# Save both JSON and Excel
python main.py --save-xlsx

# Get 72 hours of AFAD data without generating a map
python main.py --hours 72 --no-map

# Generate Marmara region magnitude-time chart along with the map
python main.py --marmara-chart

# Only generate the Marmara region magnitude-time chart
python main.py --only-marmara-chart
```

## Visualizations

### Interactive Maps

The map visualizations use Leaflet.js or Folium to display earthquakes on an interactive map:
- Earthquakes are shown as circles with size and color based on magnitude
- Hover or click on a circle to see details about each earthquake
- A legend explains the color coding of magnitudes

### Magnitude-Time Charts

These visualizations show earthquake magnitudes over time:
- Earthquakes are plotted as points on a scatter chart
- X-axis shows the date/time
- Y-axis shows the magnitude
- Points are color-coded by magnitude range

## Marmara Region Definition

The Marmara region is defined as the geographic area within these boundaries:
- Latitude: 39.5°N to 41.5°N
- Longitude: 26.0°E to 31.0°E

This covers the Sea of Marmara and surrounding provinces.

## Data Processing Details

### Time Zones
- Kandilli data is already in Turkey local time (UTC+3)
- AFAD data is provided in UTC and converted to Turkey local time (UTC+3) by the script

### Deduplication Method
Since both sources may report the same earthquakes, the system implements a deduplication method:
- Earthquakes within 60 seconds of each other
- Within 0.1 degrees (approximately 11km) distance
- With magnitude difference less than 0.5
are considered potential duplicates and merged.

## Output Format

The output files contain records with these fields:
- `eventID`: Unique identifier for the earthquake
- `date`: Date and time of the earthquake in ISO format (with timezone correction)
- `latitude`: Latitude coordinate
- `longitude`: Longitude coordinate
- `depth`: Depth in kilometers
- `magnitude`: Earthquake magnitude
- `magnitude_details`: Object containing MD, ML, and MW values (in JSON)
- In Excel, magnitude values are expanded to separate columns: `magnitude_md`, `magnitude_ml`, `magnitude_mw`
- `type`: Magnitude type (ML, MW, or MD)
- `location`: Location description
- `quality`: Quality of the measurement ("İLKSEL" or "REVİZE")
- `timestamp`: Unix timestamp in milliseconds
- `source`: Data source ("Kandilli" or "AFAD")
- Additional fields from AFAD include: `country`, `province`, `district`, and `neighborhood` 