import streamlit as st

def sidebar_component():
    """
    Composant Sidebar complet avec Recherche Géographique + Paramètres Grid
    """
    with st.sidebar:
        
        # --- SECTION 0 : RECHERCHE ---
        st.header("📍 Localisation Cible")
        
        search_query = st.text_input(
            "Point de départ du Grid",
            placeholder="Ex: Lino, 95585...",
            help="Saisissez une adresse ou un nom pour centrer l'analyse.",
            key="search_input"
        )
        
        st.caption("Laissez vide pour une 'Vue Globale'.")
        st.markdown("---")
        
        # --- SECTION 1 : SIMULATION TEMPORELLE ---
        #st.header("🕒 Simulation")
        
        #st.slider(
        #    "Heure de la journée", 
        #    min_value=0, max_value=23, value=19, 
        #    format="%dh",
        #    key="sim_hour"
        #)
        
        #st.radio(
        #    "Saison", 
        #    ["Hiver", "Été"], 
        #    horizontal=True,
         #   key="season"
        #)
        
        #st.markdown("---")

        # --- SECTION 2 : PARAMÈTRES DU GRID ---
        st.header("⚙️ Critères de Clustering")
        
        # Groupe 1 : Topologie
        with st.expander("📐 Topologie & Rayon", expanded=True):
            
            # Distance de connexion (Câblage) - Renvoie un tuple (min, max)
            dist_range = st.slider(
                "Distance liaison Grid (m)",
                min_value=0, max_value=500, value=(1, 100),
                help="Filtre les bâtiments selon leur distance au segment de réseau."
            )
            
            # Rayon d'analyse
            search_radius = st.slider(
                "Rayon d'analyse (m)",
                min_value=100, max_value=2000, value=500,
                step=100,
                help="Rayon de recherche autour de l'adresse cible."
            )
            
            min_buildings = st.number_input(
                "Nbre Bâtiments Min.", 
                min_value=1, max_value=50, value=1,
                step=1
            )

        # Groupe 2 : Énergie
        with st.expander("⚡ Énergie & Puissance", expanded=False):
            min_conso = st.number_input("Conso Min. (MWh/an)", min_value=0.0, value=0.0, step=5.0)
            
            # Filtre par taux d'autosuffisance
            min_autosuff = st.slider(
                "Auto-suffisance Min. (%)", 
                min_value=0, max_value=100, value=0, 
                step=5,
                help="Affiche uniquement les bâtiments/segments dépassant ce taux."
            )
            
            only_surplus = st.checkbox("Afficher seulement les surplus", value=False)

        # --- STOCKAGE DANS SESSION STATE ---
        # On prépare le dictionnaire pour le driver Neo4j
        grid_params = {
            'center_point': search_query,
            'search_radius': search_radius,
            'dist_min': dist_range[0],  # Valeur basse du slider range
            'dist_max': dist_range[1],  # Valeur haute du slider range
            'min_conso': min_conso,
            'min_autosuff': min_autosuff,
            'only_surplus': only_surplus,
            'min_buildings': min_buildings
        }
        
        # Sauvegarde pour que Home.py et le driver puissent y accéder
        st.session_state['grid_params'] = grid_params

        st.markdown("---")
        
        # --- SECTION 3 : ACTIONS ---
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Reset", use_container_width=True):
                st.rerun()
        with col2:
            if st.button("🚀 Analyser", type="primary", use_container_width=True):
                if search_query:
                    st.toast(f"Analyse sur : {search_query}", icon="📍")
                else:
                    st.toast("Mode Vue Globale activé", icon="🌍")