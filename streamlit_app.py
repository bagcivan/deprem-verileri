import streamlit as st
import pandas as pd
import numpy as np
import json
import folium
from streamlit_folium import st_folium
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import os
import io
import base64

# Fix for orjson compatibility issues
import plotly.io as pio
pio.json.config.default_engine = 'json'  # Use the standard json instead of orjson

# Import our modules
from constants import DEFAULT_AFAD_HOURS, MIN_AFAD_HOURS, MAX_AFAD_HOURS
from constants import DEFAULT_MAP_CENTER, DEFAULT_ZOOM_LEVEL, MARMARA_MAP_CENTER, MARMARA_ZOOM_LEVEL
from data_handler import fetch_earthquake_data, filter_data
from visualization import create_map, create_magnitude_time_chart, create_statistics, get_download_link

# Set page configuration
st.set_page_config(
    page_title="Türkiye Deprem Verileri",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# App title and description
st.title("Türkiye Deprem Verileri Görselleştirme")
st.markdown("""
Bu uygulama, Kandilli Rasathanesi ve AFAD'dan alınan deprem verilerini görselleştirir.
""")

# Sidebar with options
st.sidebar.header("Veri Kaynakları ve Filtreler")

# Data source options
data_sources = st.sidebar.multiselect(
    "Veri Kaynakları",
    ["Kandilli", "AFAD"],
    default=["Kandilli", "AFAD"]
)

# Time period for AFAD data
afad_hours = st.sidebar.slider(
    "AFAD Verisi İçin Saat Aralığı",
    min_value=MIN_AFAD_HOURS,
    max_value=MAX_AFAD_HOURS,
    value=DEFAULT_AFAD_HOURS,
    step=24,
    help="AFAD'dan kaç saat öncesine ait verileri çekmek istiyorsunuz?"
)

# Magnitude filter
min_magnitude = st.sidebar.slider(
    "Minimum Büyüklük",
    min_value=0.0,
    max_value=10.0,
    value=2.0,
    step=0.1,
    help="Bu değerden küçük depremler gösterilmeyecek"
)

# Region filter
region_filter = st.sidebar.selectbox(
    "Bölge Filtresi",
    ["Tüm Türkiye", "Marmara Bölgesi"],
    index=0
)

# Visualization type
tabs = st.tabs(["Harita", "Büyüklük-Zaman Grafiği", "İstatistikler", "Ham Veri"])

# Add explanation about deduplication logic
with st.sidebar.expander("Mükerrer Kayıt Temizleme Hakkında"):
    st.markdown("""
    **Deprem Verisi Temizleme Mantığı:**
    
    Aynı deprem için birden fazla kayıt olabileceğinden, mükerrer kayıtları şu kriterlere göre temizliyoruz:
    
    1. **Zaman yakınlığı:** 60 saniye içinde olan depremler
    2. **Konum yakınlığı:** 0.1 derece (yaklaşık 11km) mesafe içindeki depremler
    3. **Büyüklük benzerliği:** Büyüklük farkı 0.5'ten az olan depremler
    
    Bu üç kriter de sağlandığında, depremler aynı kabul edilip mükerrer kayıt temizleniyor.
    """)

def main():
    # Fetch data with caching (1 hour TTL)
    @st.cache_data(ttl=3600)
    def cached_fetch_data(sources, afad_hours):
        return fetch_earthquake_data(sources, afad_hours)
    
    df = cached_fetch_data(data_sources, afad_hours)
    
    # If data is available, filter and visualize
    if not df.empty:
        # Apply filters
        filtered_df = filter_data(df, min_magnitude, region_filter)
        
        # Count earthquakes
        total_earthquakes = len(filtered_df)
        
        if total_earthquakes == 0:
            st.warning(f"Seçilen filtrelere uygun deprem verisi bulunamadı. Farklı bir filtreleme deneyin.")
        else:
            st.success(f"Toplam {total_earthquakes} deprem görüntüleniyor.")
            
            # Map tab
            with tabs[0]:
                st.header("Deprem Haritası")
                
                # Set map center and zoom based on region filter
                map_center = MARMARA_MAP_CENTER if region_filter == "Marmara Bölgesi" else DEFAULT_MAP_CENTER
                zoom_level = MARMARA_ZOOM_LEVEL if region_filter == "Marmara Bölgesi" else DEFAULT_ZOOM_LEVEL
                show_bounds = region_filter == "Marmara Bölgesi"
                
                # Create map
                m = create_map(
                    filtered_df, 
                    center=map_center, 
                    zoom=zoom_level, 
                    show_marmara_bounds=show_bounds
                )
                
                # Display the map
                st_folium(m, width=1200, height=600)
            
            # Magnitude-Time Chart tab
            with tabs[1]:
                st.header("Büyüklük-Zaman Grafiği")
                
                # Create the chart
                fig = create_magnitude_time_chart(filtered_df)
                
                # Display the chart
                st.plotly_chart(fig, use_container_width=True)
            
            # Statistics tab
            with tabs[2]:
                st.header("Deprem İstatistikleri")
                
                # Create statistics
                stats_figures = create_statistics(filtered_df)
                
                # Display statistics figures
                col1, col2 = st.columns(2)
                with col1:
                    st.plotly_chart(stats_figures['sources'], use_container_width=True)
                    st.plotly_chart(stats_figures['magnitudes'], use_container_width=True)
                
                with col2:
                    st.plotly_chart(stats_figures['depths'], use_container_width=True)
                    if 'heatmap' in stats_figures:
                        st.plotly_chart(stats_figures['heatmap'], use_container_width=True)
            
            # Raw Data tab
            with tabs[3]:
                st.header("Ham Veri")
                
                # Show a sample of the data
                st.dataframe(filtered_df.sort_values('date', ascending=False))
                
                # Add download links
                st.markdown(get_download_link(filtered_df, "deprem_verileri.csv", "CSV olarak indir"), unsafe_allow_html=True)
                st.markdown(get_download_link(filtered_df, "deprem_verileri.json", "JSON olarak indir"), unsafe_allow_html=True)

if __name__ == "__main__":
    main() 