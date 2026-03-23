import streamlit as st

def aplicar_auth():
    st.markdown("""
        <style>
        /* Título de CoreDesk Grande y Centrado */
        .core-title-auth { 
            color: #0E3255; font-size: 60px; font-weight: 800; 
            text-align: center; margin-bottom: 0px; 
        }
        
        /* Contenedor del formulario centrado */
        div[data-testid="stForm"] {
            border: 1px solid #eee;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0px 4px 10px rgba(0,0,0,0.03);
            background-color: #fcfcfc;
        }

        /* Botón Iniciar Sesión (Azul #0E3255) */
        div[data-testid="stForm"] .stButton>button { 
            background-color: #0E3255 !important; 
            color: white !important; 
            border-radius: 8px; height: 3.5em; width: 100%;
            font-weight: bold; border: none; transition: 0.3s;
        }
        div[data-testid="stForm"] .stButton>button:hover {
            background-color: #1a4a7a !important;
            box-shadow: 0px 4px 12px rgba(0,0,0,0.15);
        }
        </style>
    """, unsafe_allow_html=True)