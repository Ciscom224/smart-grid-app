import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import pydeck as pdk
import os

# Import des composants personnalisés
from components.sidebar import sidebar_component
from services.neo4j_driver import get_driver
from components.map_local import render_local_map
from components.map_global import render_global_map

# =========================================================
# 1. CONFIGURATION ET STYLE
# =========================================================
st.set_page_config(
    page_title="Smart Grid Digital",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

def load_css(file_name):
    if os.path.exists(file_name):
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

load_css("assets/style.css")

# =========================================================
# 2. HELPERS (COURBES ET CALCULS)
# =========================================================
def generate_24h_curves_from_totals(total_conso, total_prod):
    """Génère des courbes simulées basées sur les volumes globaux"""
    hours = list(range(24))
    x = np.array(hours)
    
    # Profil Conso : Double Pic (Matin/Soir)
    base_conso = total_conso / 2000
    y_conso = base_conso * (1 + 0.4 * np.exp(-((x - 8)**2) / 8) + 0.6 * np.exp(-((x - 20)**2) / 8))
    
    # Profil Solaire : Cloche centrée à midi
    base_prod = total_prod / 1200
    y_prod = base_prod * (np.exp(-((x - 13)**2) / 8))
    y_prod[y_prod < 0.01] = 0
    
    return hours, y_conso, y_prod

# =========================================================
# 3. INITIALISATION DU DRIVER ET DONNÉES
# =========================================================
driver = None
try:
    driver = get_driver()
except Exception as e:
    st.error(f"Erreur de connexion Neo4j : {e}")
    st.stop()

# Appel de la Sidebar (remplit st.session_state['grid_params'])
sidebar_component()
params = st.session_state.get('grid_params', {})

# Récupération des données via le driver
data = driver.get_dashboard_data(params)

if not data:
    st.warning("⚠️ Aucun résultat. Ajustez vos filtres  ou changez d'adresse.")
    st.stop()

# =========================================================
# 4. LOGIQUE DE SÉPARATION (LOCAL VS GLOBAL)
# =========================================================
# On détecte le mode Global par la présence de la clé 'clusters'
is_global = "clusters" in data and data["clusters"] is not None

if is_global:
    kpis = data['kpi_global_cluster']
    center_info = data['centre']
    title = "🌍 Analyse Territoriale (Vue par Clusters)"
    label_mixite = "Clusters Détectés"
    # VALEUR CORRIGÉE : On compte le nombre d'entrées dans le dictionnaire clusters
    valeur_mixite = len(data["clusters"]) 
else:
    kpis = data['kpi']
    center_info = data['centre']
    title = f"🏠 Cluster Local : {center_info['adresse']}"
    label_mixite = "Bâtiments Prosumers"
    # VALEUR LOCALE : On prend le nombre de prosumers du cluster local
    valeur_mixite = kpis.get('nb_prosumers', 0)

# =========================================================
# 5. AFFICHAGE DU DASHBOARD
# =========================================================
st.title(title)
st.markdown(f"**{kpis['nb_batiments']} bâtiments analysés**")

# --- A. SECTION KPI ---
kpi_html = f"""
<div class="kpi-container">
    <div class="kpi-card">
        <div class="kpi-label">Consommation Totale</div>
        <div class="kpi-value c-red">{kpis['total_conso']:,.1f} MWh</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-label">Production Solaire</div>
        <div class="kpi-value c-green">{kpis['total_prod']:,.1f} MWh</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-label">Auto-suffisance</div>
        <div class="kpi-value c-purple">{kpis['autosuffisance']:.1f} %</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-label">Nbre de {label_mixite}</div>
        <div class="kpi-value c-orange">{valeur_mixite}</div>
    </div>
</div>
"""
st.markdown(kpi_html, unsafe_allow_html=True)

# --- B. SECTION GRAPHIQUES ---
col_chart1, col_chart2 = st.columns([2, 1])

with col_chart1:
    st.markdown('<div class="chart-box">', unsafe_allow_html=True)
    st.subheader("📈 Profil Énergétique Estimé (24h)")
    h, yc, yp = generate_24h_curves_from_totals(kpis['total_conso'], kpis['total_prod'])
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=h, y=yc, name='Consommation', fill='tozeroy', line=dict(color='#FF5A5F', width=3)))
    fig.add_trace(go.Scatter(x=h, y=yp, name='Production Solaire', line=dict(color='#00CC96', width=3, dash='dash')))
    
    # Ligne de l'heure actuelle (simulation)
    current_h = st.session_state.get('sim_hour', 12)
    fig.add_vline(x=current_h, line_width=2, line_dash="dot", line_color="white")
    
    fig.update_layout(template="plotly_dark", height=350, margin=dict(l=10, r=10, t=30, b=10), legend=dict(orientation="h", y=1.1))
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_chart2:
    st.markdown('<div class="chart-box">', unsafe_allow_html=True)
    st.subheader("📊 Répartition")
    
    nb_pro = kpis.get('nb_prosumers', 0)
    nb_cons = kpis['nb_batiments'] - nb_pro
    
    fig_pie = go.Figure(data=[go.Pie(
        labels=['Producteurs/Prosumers', 'Consommateurs purs'],
        values=[nb_pro, nb_cons],
        hole=.6,
        marker=dict(colors=['#00CC96', '#FF5A5F'])
    )])
    fig_pie.update_layout(template="plotly_dark", height=350, showlegend=False)
    st.plotly_chart(fig_pie, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- C. SECTION CARTE (DYNAMIQUE) ---
st.markdown("---")
st.subheader("🗺️ Cartographie du Smart Grid")

if is_global:
    # On passe le dictionnaire de clusters au composant global
    render_global_map(data["clusters"])
else:
    # On passe la liste de bâtiments et le centre au composant local
    render_local_map(data["liste_batiments"], data["centre"])

st.caption("Astuce : Survolez les points pour voir les détails de consommation et d'injection.")