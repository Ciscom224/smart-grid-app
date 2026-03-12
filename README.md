# ⚡ Smart Grid Digital Twin (Jumeau Numérique)

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28%2B-ff4b4b)
![Neo4j](https://img.shields.io/badge/Neo4j-5.x-00cc96)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4-green)

Une application de **SMART-GRID-APP** pour la gestion et la visualisation de réseaux électriques intelligents. Ce projet combine la puissance des **Bases de Données de Graphes (Neo4j)** pour la topologie, et l'**Intelligence Artificielle Générative (RAG)** pour l'assistance à l'exploitation.

---

## 📸 Aperçu

| Dashboard Global | Assistant IA (Graph RAG) |
|:---:|:---:|
| ![Dashboard Screenshot](https://via.placeholder.com/400x200?text=Dashboard+Visual) | ![Chat Screenshot](https://via.placeholder.com/400x200?text=Assistant+IA) |
*(Ajoutez ici vos captures d'écran de l'application)*

---

# 🚀 Fonctionnalités

* **Vue Territoriale (Global) :** Analyse par clusters IRIS et segments de réseau Enedis avec encerclement visuel (Halos) pour identifier les communautés énergétiques.
* **Vue Focus (Local) :** Détail granulaire par bâtiment (Consommation vs Production solaire) autour d'un point d'intérêt.
* **Graphiques Temps Réel :** Courbes de charge (24h) et typologies de clusters générées dynamiquement via Plotly.
* **Architecture Géo-Graph :** Utilisation de Neo4j pour modéliser les relations topologiques entre le réseau électrique et le bâtiment.
---

## 🛠️ Stack Technique

* **Frontend :** [Streamlit](https://streamlit.io/)
* **Base de Données :** [Neo4j](https://neo4j.com/) (Graph Database)
* **Cartographie :** [Pydeck](https://deckgl.readthedocs.io/) (Mapbox GL)
* **Visualisation :** [Plotly](https://plotly.com/python/)
* **Langage :** Python 3.10+

---

## 📂 Structure du Projet

```text
smart-grid-app/
│
├── .streamlit/           # Configuration secrète et thème
│   └── secrets.toml      # Clés API (NE PAS COMMIT)
├── assets/               # Ressources statiques
│   └── style.css         # CSS personnalisé (Dark Mode)
├── queries/              # Les requetes de clustering
│   ├── global_query.cypher             
│   └── local_query.cypher        
├── components/           # Composants UI réutilisables
│   └── sidebar.py        # Barre latérale de navigation
├── pages/                # Pages de l'application
│   ├── 1_🌍_home.py
├── services/             # Logique métier (Backend)
│   └── neo4j_driver.py   # Gestionnaire de connexion BDD
├── data/                 # Données sources (JSON/CSV)
├── Home.py               # Point d'entrée de l'application
└── requirements.txt      # Dépendances Python

```
## 📥 Installation

1.  **Cloner le dépôt :**
    ```bash
    git clone [https://github.com/votre-compte/smart-grid-twin.git](https://github.com/votre-compte/smart-grid-twin.git)
    cd smart-grid-twin
    ```

2.  **Installer les dépendances :**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configurer les secrets :**
    Créez un fichier `.streamlit/secrets.toml` à la racine :
    ```toml
    NEO4J_URI = "bolt://localhost:7687"
    NEO4J_USER = "neo4j"
    NEO4J_PASSWORD = "votre_mot_de_passe"
    ```

4.  **Lancer l'application :**
    ```bash
    streamlit run Home.py
    ```

## 👥 Auteurs

* **CISSE Mamadou** [@ciscom224](https://github.com/Ciscom224)
* **MANKAI Latifa** [@latifa](https://github.com/latifa)
* **Nom Prénom** - *Développement Streamlit & DataViz* - [@votreusername](https://github.com/votreusername)

---
*Ce projet a été développé pour optimiser la planification énergétique locale et favoriser la transition vers des réseaux bas-carbone.*