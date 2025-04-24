# Constants for the earthquake visualization application

# Define the Marmara region coordinates (approximate boundaries)
MARMARA_BOUNDS = {
    'min_lat': 39.5,  # South boundary
    'max_lat': 41.5,  # North boundary
    'min_lon': 26.0,  # West boundary
    'max_lon': 31.0   # East boundary
}

# Color mapping for earthquake magnitudes
MAGNITUDE_COLORS = {
    'very_low': '#91cf60',    # < 2.0 (green)
    'low': '#d9ef8b',         # 2.0 - 2.9 (light green)
    'moderate': '#fee08b',    # 3.0 - 3.9 (yellow)
    'high': '#fc8d59',        # 4.0 - 4.9 (orange)
    'very_high': '#d73027',   # ≥ 5.0 (red)
}

# Magnitude ranges for visualization
MAGNITUDE_RANGES = [
    {'min': 0, 'max': 2.0, 'color': MAGNITUDE_COLORS['very_low'], 'label': '< 2.0'},
    {'min': 2.0, 'max': 3.0, 'color': MAGNITUDE_COLORS['low'], 'label': '2.0 - 2.9'},
    {'min': 3.0, 'max': 4.0, 'color': MAGNITUDE_COLORS['moderate'], 'label': '3.0 - 3.9'},
    {'min': 4.0, 'max': 5.0, 'color': MAGNITUDE_COLORS['high'], 'label': '4.0 - 4.9'},
    {'min': 5.0, 'max': 10.0, 'color': MAGNITUDE_COLORS['very_high'], 'label': '≥ 5.0'},
]

# Map visualization settings
DEFAULT_MAP_CENTER = [38.9637, 35.2433]
DEFAULT_ZOOM_LEVEL = 5
MARMARA_MAP_CENTER = [40.5, 28.5]
MARMARA_ZOOM_LEVEL = 7

# Time constants
DEFAULT_AFAD_HOURS = 48
MAX_AFAD_HOURS = 168
MIN_AFAD_HOURS = 24

# API URLs
KANDILLI_BASE_URL = "http://www.koeri.boun.edu.tr/scripts/lst"
AFAD_API_URL = "https://servisnet.afad.gov.tr/apigateway/deprem/apiv2/event/filter" 