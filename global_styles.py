import streamlit as st

def aplicar_globales():
    st.markdown("""
        <style>
        /* Fondo Blanco Puro */
        .stApp { background-color: #FFFFFF; }
        
        /* Tipografía Profesional (Sans Serif) */
        html, body, [class*="st-"] {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            color: #262730;
        }

        /* Ocultar elementos nativos de Streamlit */
        div[data-testid="stHeader"], div[data-testid="stSidebarNav"] { display: none; }
        
        /* Spinner de carga color CoreDesk (Azul #0E3255) */
        .stSpinner > div { border-top-color: #0E3255 !important; }
        </style>
    """, unsafe_allow_html=True)