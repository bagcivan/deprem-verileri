import requests
import json
from datetime import datetime, timedelta
from constants import AFAD_API_URL

def get_afad_data(start_date, end_date):
    """
    Fetches earthquake data from AFAD API.
    
    Args:
        start_date: Start date in format YYYY-MM-DD HH:MM:SS
        end_date: End date in format YYYY-MM-DD HH:MM:SS
    
    Returns:
        List of earthquake data dictionaries
    """
    # Format dates for the API
    start_formatted = start_date.replace(" ", "%20")
    end_formatted = end_date.replace(" ", "%20")
    
    url = f"{AFAD_API_URL}?start={start_formatted}&end={end_formatted}"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            
            # Add source field to each earthquake
            for quake in data:
                quake["source"] = "AFAD"
            
            return data
        else:
            print(f"Error fetching AFAD data: {response.status_code}")
            return []
    except Exception as e:
        print(f"Error fetching AFAD data: {e}")
        return []

def standardize_afad_data(afad_data):
    """
    Standardizes AFAD data to match our unified format.
    """
    standardized = []
    
    for quake in afad_data:
        standardized_quake = _standardize_afad_quake(quake)
        if standardized_quake:
            standardized.append(standardized_quake)
    
    # Sort by timestamp (newest first)
    standardized.sort(key=lambda x: x.get("timestamp", 0), reverse=True)
    
    return standardized

def _standardize_afad_quake(quake):
    """
    Standardize a single AFAD earthquake entry
    
    Args:
        quake: Dictionary with AFAD earthquake data
    
    Returns:
        Dictionary with standardized earthquake data or None if standardization failed
    """
    try:
        # Parse date to get timestamp (AFAD provides UTC time)
        date_obj = datetime.fromisoformat(quake.get("date").replace('Z', '+00:00'))
        
        # Add 3 hours to convert from UTC to Turkey local time (UTC+3)
        local_date_obj = date_obj + timedelta(hours=3)
        
        # Update the date string to local time
        local_date_str = local_date_obj.strftime("%Y-%m-%dT%H:%M:%S")
        
        # Get the timestamp in milliseconds
        timestamp = int(local_date_obj.timestamp() * 1000)
        
        # Extract magnitude type and value
        mag_type = quake.get("type", "ML")
        mag_value = float(quake.get("magnitude", 0))
        
        # Create magnitude details object
        magnitude_details = {
            "md": mag_value if mag_type == "MD" else None,
            "ml": mag_value if mag_type == "ML" else None,
            "mw": mag_value if mag_type == "MW" else None
        }
        
        return {
            "eventID": quake.get("eventID"),
            "date": local_date_str,
            "latitude": float(quake.get("latitude")),
            "longitude": float(quake.get("longitude")),
            "depth": float(quake.get("depth")),
            "magnitude": mag_value,
            "magnitude_details": magnitude_details,
            "type": mag_type,
            "location": quake.get("location"),
            "country": quake.get("country"),
            "province": quake.get("province"),
            "district": quake.get("district"),
            "neighborhood": quake.get("neighborhood"),
            "timestamp": timestamp,
            "quality": "İLKSEL" if not quake.get("isEventUpdate", False) else "REVİZE",
            "source": "AFAD"
        }
    except Exception as e:
        print(f"Error standardizing AFAD data: {e}")
        return None 