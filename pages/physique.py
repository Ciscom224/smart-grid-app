import streamlit as st
import pandas as pd
import pydeck as pdk
import os

# Import des composants internes
from components.sidebar import sidebar_component
from services.neo4j_driver import get_driver

# --- 1. CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="Réseau Physique", 
    page_icon="🔌", 
    layout="wide"
)

# Chargement du CSS
def load_css(file_name):
    if os.path.exists(file_name):
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

load_css("assets/style.css")

# --- 2. BARRE LATÉRALE ---
sidebar_component()

# Récupération des paramètres (Dictionnaire complet)
params = st.session_state.get('grid_params', {})
search_query = params.get('center_point', "LINO")
radius = params.get('search_radius', 500)

# --- 3. RÉCUPÉRATION DES DONNÉES ---
try:
    driver = get_driver()
    # ⚠️ MAJ : On passe le dictionnaire complet 'params'
    data = driver.get_dashboard_data(params)
except Exception as e:
    st.error(f"Erreur de connexion Neo4j : {e}")
    st.stop()

# --- 4. AFFICHAGE PRINCIPAL ---

# Gestion du titre selon le mode
if not data or not data.get('centre') or not data['centre'].get('adresse') or data['centre']['adresse'] == "Vue Globale":
    display_title = "Vue Globale (Tout le Réseau)"
else:
    display_title = f"{search_query}"

st.title(f"🔌 Topologie Réseau : {display_title}")

if not data or not data.get('liste_batiments'):
    st.warning("⚠️ Aucune donnée trouvée. Vérifiez les filtres dans la barre latérale.")
    st.stop()

# Préparation du DataFrame
batiments = data['liste_batiments']
center = data['centre']
df_map = pd.DataFrame(batiments)

# --- 5. LOGIQUE DE VISUALISATION (PYDECK) ---

# A. Couleurs : Vert (Prosumer) / Rouge (Consumer)
def get_color(types):
    if 'Prosumer' in types: 
        return [0, 204, 150, 200] # Vert
    return [255, 90, 95, 200]     # Rouge

df_map['color'] = df_map['type'].apply(get_color)

# B. Indicateurs
c1, c2, c3 = st.columns(3)
nb_pro = df_map['type'].apply(lambda x: 'Prosumer' in x).sum()
nb_con = len(df_map) - nb_pro

with c1: st.info(f"🔴 **Consumers** : {nb_con}")
with c2: st.success(f"🟢 **Prosumers** : {nb_pro}")
with c3: 
    # Affichage sécurisé des coordonnées (peut être null en vue globale)
    lat_disp = f"{center['lat']:.4f}" if center['lat'] else "-"
    lon_disp = f"{center['lon']:.4f}" if center['lon'] else "-"
    st.caption(f"📍 Centre : {lat_disp}, {lon_disp}")

# C. Construction de la Carte
layer_batiments = pdk.Layer(
    "ScatterplotLayer",
    df_map,
    get_position=["lon", "lat"],
    get_color="color",
    get_radius=6,  # Taille fixe (6m)
    pickable=True,
    auto_highlight=True,
    opacity=0.9,
    stroked=True,
    filled=True,
    line_width_min_pixels=1,
    get_line_color=[255, 255, 255]
)

# ⚠️ GESTION DU CENTRAGE (Mode Local vs Global)
if center['lat'] is not None:
    # Mode Local : on centre sur le bâtiment recherché
    view_lat = center['lat']
    view_lon = center['lon']
    view_zoom = 16
else:
    # Mode Global : on centre sur la moyenne des points affichés
    view_lat = df_map['lat'].mean()
    view_lon = df_map['lon'].mean()
    view_zoom = 13

view_state = pdk.ViewState(
    latitude=view_lat,
    longitude=view_lon,
    zoom=view_zoom,
    pitch=0, # Vue à plat (2D)
    bearing=0
)

r = pdk.Deck(
    layers=[layer_batiments],
    initial_view_state=view_state,
    tooltip={
        "html": "<b>Adresse:</b> {adresse}<br/>"
                "<b>Type:</b> {type}<br/>"
                "<b>Conso:</b> {conso} MWh<br/>"
                "<b>Dist. Grid:</b> {dist_grid}m",
        "style": {"backgroundColor": "steelblue", "color": "white"}
    },
    map_style="mapbox://styles/mapbox/dark-v10"
)

st.pydeck_chart(r, use_container_width=True)

# --- 6. TABLEAU ---
with st.expander("📋 Voir les données brutes"):
    st.dataframe(
        df_map[['adresse', 'type', 'conso', 'prod', 'dist_grid']],
        use_container_width=True
    )