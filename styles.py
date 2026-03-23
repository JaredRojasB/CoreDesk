import streamlit as st

def aplicar_estilos():
    st.markdown("""
        <style>
        .stApp { background-color: #f4f7f9; }
        .core-title { color: #0E3255; font-size: 55px; font-weight: 800; text-align: center; margin-bottom: 0px; }
        .stButton>button { border-radius: 10px; font-weight: bold; transition: 0.3s; }
        /* Botón Iniciar Sesión */
        div[data-testid="stForm"] .stButton>button { background-color: #0E3255; color: white; height: 3.5em; width: 100%; }
        /* Botón Finalizar Rojo */
        .btn-finalizar > button {
            background-color: #d9534f !important;
            color: white !important;
            border: none !important;
        }
        .stSpinner > div { border-top-color: #0E3255 !important; }
        </style>
    """, unsafe_allow_html=True)