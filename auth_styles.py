import streamlit as st

def aplicar_auth():
    st.markdown("""
        <style>
        .stApp { background-color: #FFFFFF; }
        .core-title-auth { 
            color: #0E3255; font-size: 50px; font-weight: 800; 
            text-align: center; margin-bottom: 10px; 
        }
        div[data-testid="stForm"] {
            border: 1px solid #eee; border-radius: 12px;
            padding: 30px; box-shadow: 0px 4px 15px rgba(0,0,0,0.05);
        }
        div[data-testid="stForm"] .stButton>button { 
            background-color: #0E3255 !important; color: white !important; 
            border-radius: 8px; height: 3.5em; width: 100%; font-weight: bold;
        }
        /* Ocultar basura de Streamlit */
        div[data-testid="stHeader"], .st-emotion-cache-1ae8k9u { display: none !important; }
        </style>
    """, unsafe_allow_html=True)