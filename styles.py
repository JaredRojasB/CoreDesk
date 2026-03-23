import streamlit as st

def aplicar_estilos_globales():
    """Estilos para toda la aplicación"""
    st.markdown("""
        <style>
        .stApp { background-color: #FFFFFF; }
        html { font-size: 16px; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        div[data-testid="stHeader"], div[data-testid="stSidebarNav"] { display: none; }
        .stSpinner > div { border-top-color: #0E3255 !important; }
        </style>
    """, unsafe_allow_html=True)

def aplicar_estilos_inicio():
    """Estilos específicos para la pantalla de Login"""
    st.markdown("""
        <style>
        .core-title-main { 
            color: #0E3255; font-size: 60px; font-weight: 800; 
            text-align: center; margin-bottom: 0px; 
        }
        
        div[data-testid="stForm"] .stButton>button { 
            background-color: #0E3255 !important; 
            color: white !important; 
            border-radius: 8px; height: 3.5em; width: 100%;
            font-weight: bold; border: none;
            transition: 0.3s;
        }
        div[data-testid="stForm"] .stButton>button:hover {
            background-color: #1a4a7a !important;
            box-shadow: 0px 4px 10px rgba(0,0,0,0.1);
        }
        </style>
    """, unsafe_allow_html=True)