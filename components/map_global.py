import streamlit as st
import pydeck as pdk
import pandas as pd

def render_global_map(clusters_dict):
    all_buildings = []
    cluster_centers = []

    # 1. Extraction des données
    for c_id, c_data in clusters_dict.items():
        kpi = c_data["Kpi"]
        liste_b = c_data["liste_batiments"]
        
        # Définition de la couleur du cluster (basée sur l'autosuffisance)
        ratio = kpi["autosuffisance"]
        if ratio >= 60: color = [0, 255, 150]   # Vert
        elif ratio >= 25: color = [255, 165, 0] # Orange
        else: color = [255, 90, 95]             # Rouge

        # On stocke le centre du cluster pour le Halo (cercle)
        # On utilise les coordonnées du premier bâtiment comme centre du cercle
        cluster_centers.append({
            "name": kpi["nom"],
            "lat": liste_b[0]["lat"],
            "lon": liste_b[0]["lon"],
            "color": color,
            "autosuffisance": ratio,
            "iris": kpi.get("iris", "N/A"),
            "conso": kpi["total_conso"],
            "nb_batiments": kpi["nb_batiments"]
        })

        # On ajoute chaque bâtiment individuel à la liste globale
        for b in liste_b:
            all_buildings.append({
                "lat": b["lat"],
                "lon": b["lon"],
                "adresse": b["adresse"],
                "conso": b["conso"],
                "prod": b["prod"],
                # Couleur du point bâtiment : vert si prod, rouge si conso pure
                "b_color": [0, 204, 150] if b["prod"] > 0.1 else [255, 90, 95]
            })

    # Conversion en DataFrames
    df_buildings = pd.DataFrame(all_buildings)
    df_clusters = pd.DataFrame(cluster_centers)

    # 2. État de la vue
    view_state = pdk.ViewState(
        latitude=df_buildings['lat'].mean(),
        longitude=df_buildings['lon'].mean(),
        zoom=12,
        pitch=0
    )

    # 3. Définition des Couches
    layers = [
        # COUCHE 1 : Les Halos d'encerclement (Zones de clusters)
        pdk.Layer(
            "ScatterplotLayer",
            df_clusters,
            get_position=["lon", "lat"],
            get_fill_color="none",
            get_radius=90, # Rayon de l'encerclement en mètres
            opacity=0.15,
            pickable=True,
            stroked=True,
            line_width_min_pixels=2,
            get_line_color="color"
        ),
        
        # COUCHE 2 : Tous les bâtiments (Petits points)
        pdk.Layer(
            "ScatterplotLayer",
            df_buildings,
            get_position=["lon", "lat"],
            get_fill_color="b_color",
            get_radius=20, # Très petits points pour ne pas saturer
            opacity=0.8,
            pickable=True
        )
    ]

    # 4. Affichage
    st.pydeck_chart(pdk.Deck(
        layers=layers,
        initial_view_state=view_state,
        tooltip={
            "html": """
            <div style="background: #1E1E1E; color: white; padding: 8px; border-radius: 5px;">
                <b>{name}</b><br/>
                <b>{adresse}</b><br/>
                <b>Nombre de batiments: {nb_batiments}<br/>
                 <b>conso : {conso}</b><br/>
                <b>Autosuffisance:{autosuffisance} %<br/>
            </div>
            """,
            "style": {"backgroundColor": "transparent", "color": "white"}
        },
        map_style="mapbox://styles/mapbox/dark-v10"
    ))