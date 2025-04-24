import pandas as pd
from datetime import datetime, timedelta
import streamlit as st
from kandilli import get_kandilli_data, parse_kandilli_data
from afad import get_afad_data, standardize_afad_data
from utils import deduplicate_earthquakes
from constants import DEFAULT_AFAD_HOURS

def fetch_earthquake_data(sources, afad_hours=DEFAULT_AFAD_HOURS):
    """
    Fetch earthquake data from selected sources
    
    Args:
        sources: List of data sources to fetch from ["Kandilli", "AFAD"]
        afad_hours: Number of hours to fetch from AFAD
    
    Returns:
        DataFrame with standardized earthquake data
    """
    combined_data = []
    
    # Get Kandilli data if selected
    if "Kandilli" in sources:
        with st.spinner('Kandilli verisi alınıyor...'):
            kandilli_html = get_kandilli_data()
            if kandilli_html:
                kandilli_data = parse_kandilli_data(kandilli_html)
                st.sidebar.success(f"{len(kandilli_data)} deprem verisi Kandilli'den alındı.")
                combined_data.extend(kandilli_data)
            else:
                st.sidebar.error("Kandilli verileri alınamadı.")
    
    # Get AFAD data if selected
    if "AFAD" in sources:
        with st.spinner('AFAD verisi alınıyor...'):
            end_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            start_date = (datetime.now() - timedelta(hours=afad_hours)).strftime("%Y-%m-%d %H:%M:%S")
            
            afad_data = get_afad_data(start_date, end_date)
            if afad_data:
                standardized_afad = standardize_afad_data(afad_data)
                st.sidebar.success(f"{len(standardized_afad)} deprem verisi AFAD'dan alındı.")
                combined_data.extend(standardized_afad)
            else:
                st.sidebar.error("AFAD verileri alınamadı.")
    
    # Deduplicate data
    if combined_data:
        unique_earthquakes = deduplicate_earthquakes(combined_data)
        st.sidebar.info(f"Mükerrer veriler temizlendi. Toplam {len(unique_earthquakes)} benzersiz deprem verisi.")
        
        # Convert to DataFrame
        df = pd.DataFrame(unique_earthquakes)
        
        # Convert date to datetime
        df['date'] = pd.to_datetime(df['date'])
        
        # Sort by date (newest first)
        df = df.sort_values('date', ascending=False)
        
        return df
    else:
        st.error("Hiç deprem verisi alınamadı.")
        return pd.DataFrame()

def filter_data(df, min_magnitude=0.0, region="Tüm Türkiye"):
    """
    Filter earthquake data based on criteria
    
    Args:
        df: DataFrame containing earthquake data
        min_magnitude: Minimum magnitude to include
        region: Region filter ("Tüm Türkiye" or "Marmara Bölgesi")
    
    Returns:
        Filtered DataFrame
    """
    from visualization import is_in_marmara_region
    
    # Filter by magnitude
    filtered_df = df.copy()  # Create a copy to avoid SettingWithCopyWarning
    filtered_df = filtered_df[filtered_df['magnitude'] >= min_magnitude]
    
    # Filter by region if Marmara is selected
    if region == "Marmara Bölgesi":
        # Create a mask for Marmara region
        marmara_mask = filtered_df.apply(
            lambda row: is_in_marmara_region(row['latitude'], row['longitude']), 
            axis=1
        )
        filtered_df = filtered_df[marmara_mask]
    
    return filtered_df 