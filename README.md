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

## 🚀 Fonctionnalités Clés

* **🌍 Dashboard Interactif** : Visualisation des KPIs temps réel (Consommation, Production Solaire, Auto-suffisance) et courbes de charge.
* **📍 Topologie Physique** : Carte interactive (Mapbox) affichant les câbles, consommateurs et producteurs avec mise en évidence dynamique.
* **🤖 Assistant Intelligent (RAG)** : Chatbot capable de "discuter" avec le réseau (ex: *"Quelle est la charge du câble rue Lino Ventura ?"*) en interrogeant la base de graphe via LangChain.
* **🕒 Simulation Temporelle** : Slider interactif pour simuler l'état du réseau à n'importe quelle heure de la journée (0h - 24h) et selon la saison.
* **🔌 Modélisation Graphe** : Gestion des relations complexes (Bâtiment -> Quartier -> Câble -> Transformateur).

---

## 🛠️ Stack Technique

* **Frontend** : [Streamlit](https://streamlit.io/) (Interface Web Python).
* **Base de Données** : [Neo4j](https://neo4j.com/) (Graph Database) pour stocker la topologie et les profils de consommation.
* **Visualisation** : [Plotly Express](https://plotly.com/python/) & Graph Objects.
* **IA & NLP** : [LangChain](https://www.langchain.com/) + OpenAI (GPT-3.5/4) pour le moteur RAG.
* **Driver** : `neo4j-python-driver` pour les requêtes Cypher.

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
│   ├── 1_🌍_Vue_Globale.py
│   └── 3_🤖_Assistant_IA.py
├── services/             # Logique métier (Backend)
│   ├── neo4j_driver.py   # Gestionnaire de connexion BDD
│   └── rag_engine.py     # Moteur d'Intelligence Artificielle
├── data/                 # Données sources (JSON/CSV)
├── Home.py               # Point d'entrée de l'application
└── requirements.txt      # Dépendances Python