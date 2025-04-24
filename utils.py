import pandas as pd
from datetime import datetime

def deduplicate_earthquakes(earthquakes):
    """
    Removes duplicate earthquakes from the combined dataset.
    
    Args:
        earthquakes: List of earthquake dictionaries
    
    Returns:
        List of deduplicated earthquake dictionaries
    """
    if not earthquakes:
        return []
    
    # Convert to DataFrame for easier manipulation
    df = pd.DataFrame(earthquakes)
    
    # Get unique earthquakes (approximately)
    # We consider earthquakes within 60 seconds and 0.1 degrees as potential duplicates
    unique_earthquakes = []
    used_indices = set()
    
    for i, row in df.iterrows():
        if i in used_indices:
            continue
            
        unique_earthquakes.append(row.to_dict())
        
        # Find potential duplicates
        for j, other_row in df.iterrows():
            if i == j or j in used_indices:
                continue
                
            # Get time difference in seconds
            time_diff = abs((row['timestamp'] - other_row['timestamp']) / 1000)  # Convert ms to seconds
            
            # Calculate distance using lat/long
            distance = (
                (row['latitude'] - other_row['latitude'])**2 + 
                (row['longitude'] - other_row['longitude'])**2
            )**0.5
            
            # Compare magnitude difference
            mag_diff = abs(row['magnitude'] - other_row['magnitude']) if not pd.isna(row['magnitude']) and not pd.isna(other_row['magnitude']) else float('inf')
            
            # If close in time, location and magnitude, consider it a duplicate
            if time_diff < 60 and distance < 0.1 and mag_diff < 0.5:
                used_indices.add(j)
    
    return unique_earthquakes

def save_to_json(data, filename='combined_earthquakes.json'):
    """
    Saves earthquake data to a JSON file.
    
    Args:
        data: List of earthquake dictionaries or DataFrame
        filename: Output filename
    """
    if isinstance(data, pd.DataFrame):
        data.to_json(filename, orient='records', date_format='iso')
    else:
        df = pd.DataFrame(data)
        df.to_json(filename, orient='records', date_format='iso')
    
    print(f"Data saved to {filename}")

def save_to_xlsx(data, filename='combined_earthquakes.xlsx'):
    """
    Saves earthquake data to an Excel file.
    
    Args:
        data: List of earthquake dictionaries or DataFrame
        filename: Output filename
    """
    if isinstance(data, pd.DataFrame):
        df = data
    else:
        df = pd.DataFrame(data)
    
    # Handle nested fields like magnitude_details
    for row_idx, row in df.iterrows():
        if 'magnitude_details' in row and isinstance(row['magnitude_details'], dict):
            for key, value in row['magnitude_details'].items():
                col_name = f"magnitude_{key}"
                df.at[row_idx, col_name] = value
    
    # Drop the original magnitude_details column
    if 'magnitude_details' in df.columns:
        df = df.drop('magnitude_details', axis=1)
    
    # Save to Excel
    df.to_excel(filename, index=False, engine='openpyxl')
    print(f"Data saved to {filename}") 