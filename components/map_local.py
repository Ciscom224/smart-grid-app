import streamlit as st
import pydeck as pdk
import pandas as pd

def render_local_map(batiments, center):
    df = pd.DataFrame(batiments)
    df['lat'] = pd.to_numeric(df['lat'])
    df['lon'] = pd.to_numeric(df['lon'])

    # Vert pour Prosumer, Rouge pour Consumer
    df['color'] = df.apply(lambda row: [0, 204, 150, 255] if 'Prosumer' in row.get('type', []) else [255, 90, 95, 255], axis=1)

    view_state = pdk.ViewState(
        latitude=center.get('lat', df['lat'].mean()),
        longitude=center.get('lon', df['lon'].mean()),
        zoom=16,
        pitch=0
    )

    layer = pdk.Layer(
        "ScatterplotLayer",
        df,
        get_position=["lon", "lat"],
        get_color="color",
        get_radius=8,
        radius_min_pixels=6,
        pickable=True,
        stroked=True,
        line_width_min_pixels=1,
        get_line_color=[255, 255, 255]
    )

    st.pydeck_chart(pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        tooltip={"html": "<b>{adresse}</b><br/>Conso: {conso} MWh<br/>Prod: {prod} MWh"},
        map_style="mapbox://styles/mapbox/dark-v10"
    ))