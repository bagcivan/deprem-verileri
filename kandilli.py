import requests
from bs4 import BeautifulSoup
from datetime import datetime
from constants import KANDILLI_BASE_URL

def get_kandilli_data():
    """
    Fetches earthquake data from Kandilli Observatory website.
    Tries lst0.asp first, and if that fails, tries lst1.asp through lst9.asp.
    """
    for i in range(10):  # Try lst0.asp through lst9.asp
        url = f"{KANDILLI_BASE_URL}{i}.asp"
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                return response.text
        except requests.RequestException:
            continue
    
    return None

def parse_kandilli_data(html_content):
    """
    Parses the HTML content from Kandilli Observatory website.
    Returns a list of dictionaries containing earthquake information.
    """
    if not html_content:
        return []
    
    soup = BeautifulSoup(html_content, 'html.parser')
    pre_text = soup.find('pre')
    
    if not pre_text:
        return []
    
    text_content = pre_text.text
    
    # Split by lines
    lines = text_content.split('\n')
    
    # Find the line with the header separator
    data_start_index = next((i for i, line in enumerate(lines) if '---------- --------' in line), -1)
    
    if data_start_index == -1:
        return []
    
    earthquakes = []
    
    for i in range(data_start_index + 1, len(lines)):
        line = lines[i].strip()
        if not line or line.startswith('---') or 'Sitemizde' in line:
            continue
        
        earthquake = _parse_kandilli_line(line)
        if earthquake:
            earthquakes.append(earthquake)
    
    # Sort by timestamp (newest first)
    earthquakes.sort(key=lambda x: x.get("timestamp", 0), reverse=True)
    
    return earthquakes

def _parse_kandilli_line(line):
    """
    Parse a single line of Kandilli data
    
    Args:
        line: A single line of text from Kandilli data
    
    Returns:
        Dictionary with parsed earthquake data or None if parsing failed
    """
    try:
        # Split by whitespace
        parts = line.split()
        
        if len(parts) >= 9:
            # Get the date and time
            date_str = parts[0]
            time_str = parts[1]
            
            # Get coordinates and depth
            lat = float(parts[2])
            lon = float(parts[3])
            depth = float(parts[4])
            
            # Get magnitude values
            md_str = parts[5]
            ml_str = parts[6]
            mw_str = parts[7]
            
            md = float(md_str) if md_str != '-.-' else None
            ml = float(ml_str) if ml_str != '-.-' else None
            mw = float(mw_str) if mw_str != '-.-' else None
            
            # Calculate the magnitude value (ML preferred, then MW, then MD)
            magnitude_value = None
            if ml is not None:
                magnitude_value = ml
            elif mw is not None:
                magnitude_value = mw
            elif md is not None:
                magnitude_value = md
            else:
                magnitude_value = 0
            
            # Get location and quality
            location_end_index = len(parts) - 1
            location = ' '.join(parts[8:location_end_index])
            quality = parts[location_end_index].replace("ILKSEL", "İLKSEL")
            
            # Format the timestamp
            timestamp = datetime.strptime(f"{date_str.replace('.', '-')}T{time_str}", "%Y-%m-%dT%H:%M:%S")
            
            # Create the earthquake object
            earthquake = {
                "eventID": f"kandilli_{date_str.replace('.', '')}_{time_str.replace(':', '')}",
                "date": timestamp.strftime("%Y-%m-%dT%H:%M:%S"),
                "latitude": lat,
                "longitude": lon,
                "depth": depth,
                "magnitude": magnitude_value,
                "magnitude_details": {
                    "md": md,
                    "ml": ml,
                    "mw": mw
                },
                "type": "ML" if ml is not None else ("MW" if mw is not None else "MD"),
                "location": location,
                "quality": quality,
                "timestamp": int(timestamp.timestamp() * 1000),  # Unix timestamp in milliseconds
                "source": "Kandilli"
            }
            
            return earthquake
    except Exception as e:
        # Skip problematic lines
        print(f"Error parsing Kandilli line: {e}")
    
    return None 