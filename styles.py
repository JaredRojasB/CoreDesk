import streamlit as st

def aplicar_estilos_globales():
    """Estilos que aplican a toda la aplicación"""
    st.markdown("""
        <style>
        /* Fondo blanco puro en toda la App */
        .stApp { background-color: #FFFFFF; }
        
        /* Tipografía responsiva y limpia */
        html { font-size: 16px; font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; }
        @media (max-width: 768px) { html { font-size: 14px; } }

        /* Spinner de carga de color de la marca (Azul CoreDesk) */
        .stSpinner > div { border-top-color: #0E3255 !important; }
        
        /* Ocultar elementos de Streamlit por defecto */
        div[data-testid="stHeader"] { display: none; }
        div[data-testid="stSidebarNav"] { display: none; }
        </style>
    """, unsafe_allow_html=True)

def aplicar_estilos_inicio():
    """Estilos específicos para la pantalla de Login"""
    st.markdown("""
        <style>
        /* Título de CoreDesk grande y centrado */
        .core-title-main { 
            color: #0E3255; font-size: 60px; font-weight: 800; 
            text-align: center; margin-bottom: 5px; 
        }
        
        /* Botón Iniciar Sesión (Azul Marino) */
        div[data-testid="stForm"] .stButton>button { 
            background-color: #0E3255 !important; 
            color: white !important; 
            border-radius: 8px; height: 3.5em; width: 100%;
            font-weight: bold; border: none;
        }
        div[data-testid="stForm"] .stButton>button:hover {
            background-color: #1a4a7a !important;
        }
        </style>
    """, unsafe_allow_html=True)