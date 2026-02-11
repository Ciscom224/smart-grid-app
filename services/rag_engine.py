# services/rag_engine.py
from langchain.chat_models import ChatOpenAI
from langchain.chains import GraphCypherQAChain
from langchain.graphs import Neo4jGraph
import streamlit as st

def get_rag_chain():
    """Initialise la chaîne de questions-réponses sur le graphe"""
    
    # 1. Connexion au Graphe pour LangChain
    graph = Neo4jGraph(
        url=st.secrets["NEO4J_URI"],
        username=st.secrets["NEO4J_USER"],
        password=st.secrets["NEO4J_PASSWORD"]
    )

    # 2. Modèle LLM (GPT-4 recommandé pour le Cypher complexe)
    llm = ChatOpenAI(
        model="gpt-4", 
        temperature=0,
        openai_api_key=st.secrets["OPENAI_API_KEY"]
    )

    # 3. Création de la chaîne RAG
    # verbose=True permet de voir la requête Cypher générée dans la console
    chain = GraphCypherQAChain.from_llm(
        llm, 
        graph=graph, 
        verbose=True,
        allow_dangerous_requests=True # Nécessaire pour les versions récentes
    )
    
    return chain

def query_graph_ai(user_question):
    """Fonction simple pour interroger l'IA"""
    try:
        chain = get_rag_chain()
        response = chain.run(user_question)
        return response
    except Exception as e:
        return f"Désolé, je n'ai pas pu analyser le graphe : {str(e)}"