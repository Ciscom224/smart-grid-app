from neo4j import GraphDatabase
import streamlit as st
import os

class Neo4jConnector:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        if self.driver:
            self.driver.close()

    def _load_query(self, filename):
        """Charge le fichier Cypher depuis le dossier queries"""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Correction : On pointe vers le dossier 'queries' à la racine
        file_path = os.path.join(current_dir, '..', 'queries', filename)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except FileNotFoundError:
            st.error(f"Fichier Cypher introuvable : {file_path}")
            return None

    def get_dashboard_data(self, grid_params):
        """
        Récupère les données selon le mode (Local si adresse saisie, Global sinon)
        """
        search_term = grid_params.get('center_point', "")
        
        # --- CHOIX DU FICHIER CYPHER ---
        # Si search_term n'est pas vide, on utilise la logique locale (par bâtiment)
        # Sinon, on utilise la logique globale (par segment de réseau)
        is_local = bool(search_term and search_term.strip())
        query_file = 'local_query.cypher' if is_local else 'global_query.cypher'
        
        query = self._load_query(query_file)
        if not query:
            return None

        # --- PARAMÈTRES ---
        params = {
            "search_term": search_term,
            "radius": grid_params.get('search_radius', 500),
            "dist_min": grid_params.get('dist_min', 0),
            "dist_max": grid_params.get('dist_max', 100),
            "min_conso": grid_params.get('min_conso', 0.0),
            "min_autosuff": grid_params.get('min_autosuff', 0),
            "min_buildings": grid_params.get('min_buildings', 1)
        }

        # --- EXÉCUTION ---
        with self.driver.session() as session:
            try:
                result = session.run(query, **params).single()
                if result and result.get("Resultat"):
                    return result["Resultat"]
                else:
                    # Cas où la requête ne trouve aucun cluster mixte (au moins 1 consumer)
                    return None
            except Exception as e:
                st.error(f"Erreur lors de l'exécution de {query_file} : {e}")
                return None

# --- Singleton pour Streamlit ---
@st.cache_resource
def get_driver():
    # Récupération sécurisée des accès via secrets.toml
    uri = st.secrets.get("NEO4J_URI", "bolt://localhost:7687")
    user = st.secrets.get("NEO4J_USER", "neo4j")
    password = st.secrets.get("NEO4J_PASSWORD", "password")
    return Neo4jConnector(uri, user, password)