import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import folium
from folium.plugins import MarkerCluster
import base64
import io
from constants import MAGNITUDE_COLORS, MAGNITUDE_RANGES
from constants import DEFAULT_MAP_CENTER, DEFAULT_ZOOM_LEVEL, MARMARA_BOUNDS

def is_in_marmara_region(lat, lon):
    """
    Check if a point is within the Marmara region based on coordinates.
    """
    return (MARMARA_BOUNDS['min_lat'] <= lat <= MARMARA_BOUNDS['max_lat'] and
            MARMARA_BOUNDS['min_lon'] <= lon <= MARMARA_BOUNDS['max_lon'])

def get_magnitude_color(magnitude):
    """
    Return color based on earthquake magnitude
    """
    if magnitude >= 5.0:
        return MAGNITUDE_COLORS['very_high']
    elif magnitude >= 4.0:
        return MAGNITUDE_COLORS['high']
    elif magnitude >= 3.0:
        return MAGNITUDE_COLORS['moderate']
    elif magnitude >= 2.0:
        return MAGNITUDE_COLORS['low']
    else:
        return MAGNITUDE_COLORS['very_low']

def create_map(df, center=DEFAULT_MAP_CENTER, zoom=DEFAULT_ZOOM_LEVEL, show_marmara_bounds=False):
    """
    Create an interactive folium map with earthquake data
    
    Args:
        df: DataFrame containing earthquake data
        center: Center coordinates for map [lat, lon]
        zoom: Initial zoom level for map
        show_marmara_bounds: Whether to display Marmara region boundary
    
    Returns:
        folium.Map object
    """
    # Create the map
    m = folium.Map(location=center, zoom_start=zoom, tiles="OpenStreetMap")
    
    # Create a marker cluster
    marker_cluster = folium.plugins.MarkerCluster().add_to(m)
    
    # If showing Marmara region, add rectangle boundary
    if show_marmara_bounds:
        folium.Rectangle(
            bounds=[
                [MARMARA_BOUNDS['min_lat'], MARMARA_BOUNDS['min_lon']], 
                [MARMARA_BOUNDS['max_lat'], MARMARA_BOUNDS['max_lon']]
            ],
            color='blue',
            fill=True,
            fill_opacity=0.1,
            tooltip='Marmara Bölgesi Sınırları'
        ).add_to(m)
    
    # Add markers for each earthquake
    for _, row in df.iterrows():
        magnitude = row['magnitude']
        color = get_magnitude_color(magnitude)
        
        # Create popup with earthquake information
        popup_html = f"""
        <strong>{row['location']}</strong><br>
        Büyüklük: {magnitude:.1f}<br>
        Derinlik: {row['depth']:.1f} km<br>
        Tarih: {row['date'].strftime('%Y-%m-%d %H:%M:%S')}<br>
        Kaynak: {row['source']}
        """
        
        # Add a circle marker for each earthquake
        folium.CircleMarker(
            location=[row['latitude'], row['longitude']],
            radius=magnitude * 2,  # Size proportional to magnitude
            color='black',
            weight=1,
            fill=True,
            fill_color=color,
            fill_opacity=0.7,
            popup=folium.Popup(popup_html, max_width=300)
        ).add_to(marker_cluster)
    
    # Add legend
    legend_html = '''
    <div style="position: fixed; 
                bottom: 50px; right: 50px; width: 150px; height: 170px; 
                border:2px solid grey; z-index:9999; background-color:white;
                padding: 10px;
                font-size: 14px;
                ">
      <p><b>Büyüklük</b></p>
      <p><i style="background: #91cf60; width: 15px; height: 15px; display: inline-block;"></i> &lt; 2.0</p>
      <p><i style="background: #d9ef8b; width: 15px; height: 15px; display: inline-block;"></i> 2.0 - 2.9</p>
      <p><i style="background: #fee08b; width: 15px; height: 15px; display: inline-block;"></i> 3.0 - 3.9</p>
      <p><i style="background: #fc8d59; width: 15px; height: 15px; display: inline-block;"></i> 4.0 - 4.9</p>
      <p><i style="background: #d73027; width: 15px; height: 15px; display: inline-block;"></i> ≥ 5.0</p>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))
    
    return m

def create_magnitude_time_chart(df):
    """
    Create a scatter plot showing earthquake magnitudes over time
    
    Args:
        df: DataFrame containing earthquake data
    
    Returns:
        plotly figure object
    """
    # Create a basic scatter plot
    fig = px.scatter(
        df, 
        x='date', 
        y='magnitude',
        color='magnitude',
        size='magnitude',  
        size_max=15,
        color_continuous_scale=[
            [0, MAGNITUDE_COLORS['very_low']],
            [0.2, MAGNITUDE_COLORS['very_low']], 
            [0.2, MAGNITUDE_COLORS['low']],
            [0.4, MAGNITUDE_COLORS['low']],
            [0.4, MAGNITUDE_COLORS['moderate']],
            [0.6, MAGNITUDE_COLORS['moderate']],
            [0.6, MAGNITUDE_COLORS['high']],
            [0.8, MAGNITUDE_COLORS['high']],
            [0.8, MAGNITUDE_COLORS['very_high']],
            [1.0, MAGNITUDE_COLORS['very_high']]
        ],
        hover_data={
            'date': True,
            'magnitude': ':.1f',
            'depth': ':.1f',
            'location': True,
            'source': True
        },
        labels={
            'date': 'Tarih',
            'magnitude': 'Büyüklük (M)',
            'depth': 'Derinlik (km)',
            'location': 'Lokasyon',
            'source': 'Kaynak'
        }
    )
    
    # Update layout for better appearance
    fig.update_layout(
        title='Deprem Büyüklükleri Zaman Grafiği',
        xaxis_title='Tarih',
        yaxis_title='Büyüklük (M)',
        coloraxis_colorbar=dict(
            title='Büyüklük (M)',
            tickvals=[1, 2, 3, 4, 5, 6],
            ticktext=['1', '2', '3', '4', '5', '6+'],
            dtick=1
        ),
        height=600
    )
    
    # Add depth reference line
    fig.add_shape(
        type="line",
        x0=df['date'].min(),
        y0=4.0,
        x1=df['date'].max(),
        y1=4.0,
        line=dict(
            color="rgba(255, 0, 0, 0.5)",
            width=1,
            dash="dash",
        )
    )
    
    # Improve temporal resolution of x-axis
    fig.update_xaxes(
        rangeslider_visible=True,
        rangeselector=dict(
            buttons=list([
                dict(count=6, label="6s", step="hour", stepmode="backward"),
                dict(count=12, label="12s", step="hour", stepmode="backward"),
                dict(count=1, label="1g", step="day", stepmode="backward"),
                dict(count=3, label="3g", step="day", stepmode="backward"),
                dict(count=7, label="1h", step="day", stepmode="backward"),
                dict(step="all", label="Hepsi")
            ]),
            font=dict(color="black"),
            bgcolor="lightgray"
        )
    )
    
    return fig

def create_statistics(df):
    """
    Create statistics visualization from earthquake data
    
    Args:
        df: DataFrame containing earthquake data
    
    Returns:
        Dict containing plotly figure objects
    """
    figures = {}
    
    # Get counts by source
    source_counts = df['source'].value_counts().reset_index()
    source_counts.columns = ['source', 'count']
    
    # Pie chart for data sources
    fig_sources = px.pie(
        source_counts, 
        values='count', 
        names='source',
        title='Veri Kaynağı Dağılımı',
        hole=0.3,
        color_discrete_sequence=px.colors.qualitative.Safe
    )
    figures['sources'] = fig_sources
    
    # Histogram for magnitudes
    fig_magnitudes = px.histogram(
        df,
        x='magnitude',
        nbins=20,
        color_discrete_sequence=['indianred'],
        title="Deprem Büyüklüğü Dağılımı"
    )
    fig_magnitudes.update_layout(
        xaxis_title="Büyüklük (M)",
        yaxis_title="Sayı"
    )
    figures['magnitudes'] = fig_magnitudes
    
    # Histogram for depths
    fig_depths = px.histogram(
        df,
        x='depth',
        nbins=20,
        color_discrete_sequence=['steelblue'],
        title="Deprem Derinliği Dağılımı"
    )
    fig_depths.update_layout(
        xaxis_title="Derinlik (km)",
        yaxis_title="Sayı"
    )
    figures['depths'] = fig_depths
    
    # Time heatmap for hour of day
    if 'date' in df.columns:
        df_time = df.copy()
        df_time['hour'] = df_time['date'].dt.hour
        df_time['day'] = df_time['date'].dt.day_name()
        
        # Count by hour and day
        hour_day_counts = df_time.groupby(['day', 'hour']).size().reset_index(name='count')
        
        # Pivot table for heatmap
        pivot_table = hour_day_counts.pivot(index='day', columns='hour', values='count')
        
        # Order days of week
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        pivot_table = pivot_table.reindex(day_order)
        
        # Create heatmap
        fig_heatmap = px.imshow(
            pivot_table,
            color_continuous_scale='YlOrRd',
            labels=dict(x="Saat", y="Gün", color="Sayı"),
            title="Depremlerin Gün ve Saatlere Göre Dağılımı"
        )
        figures['heatmap'] = fig_heatmap
    
    return figures

def get_download_link(df, filename, text):
    """
    Generate a download link for dataframe as CSV
    
    Args:
        df: DataFrame to download
        filename: Name of file to download
        text: Link text to display
    
    Returns:
        HTML string with download link
    """
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}" target="_blank">{text}</a>'
    return href 