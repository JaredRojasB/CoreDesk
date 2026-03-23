import streamlit as st

def aplicar_chat():
    st.markdown("""
        <style>
        /* --- 1. LOGO Y HEADER --- */
        .header-fixed {
            position: fixed; top: 0; left: 0; width: 100%; height: 75px;
            background: white; z-index: 999; display: flex;
            align-items: center; padding: 0 5%; border-bottom: 1px solid #EEE;
        }
        /* LOGO MÁS GRANDE */
        .logo-chat { height: 65px !important; width: auto !important; }

        /* --- 2. TARJETA FORMAL --- */
        .user-card-formal {
            background-color: #ffffff; padding: 15px 25px;
            border-radius: 12px; box-shadow: 0px 4px 15px rgba(0,0,0,0.05);
            border-left: 5px solid #0E3255; margin-bottom: 25px;
            display: flex; justify-content: space-between; align-items: center;
            margin-top: 20px;
        }

        /* --- 3. EL MÁS (+) INTEGRADO EN LA BARRA --- */
        div[data-testid="stChatInput"] {
            padding-left: 60px !important;
        }
        .stPopover {
            position: fixed !important;
            bottom: 40px !important;
            left: calc(10% + 20px) !important;
            z-index: 1001 !important;
        }
        .stPopover button { 
            background: transparent !important; 
            color: #0E3255 !important; 
            border: none !important;
            font-size: 30px !important;
            font-weight: bold !important;
        }

        /* --- 4. BOTÓN X FLOTANTE (ANIMACIÓN CORREGIDA) --- */
        #finalizar-btn-flotante {
            position: fixed; bottom: 40px; left: 40px;
            width: 70px; height: 70px; background-color: #FF4B4B;
            border-radius: 50%; display: flex; align-items: center;
            justify-content: center; box-shadow: 0px 5px 15px rgba(255, 75, 75, 0.4);
            cursor: pointer; z-index: 1002; transition: transform 0.4s ease;
            text-decoration: none; border: none;
        }
        #finalizar-btn-flotante:hover { 
            transform: scale(1.1) rotate(180deg); /* Gira sobre su propio eje */
            background-color: #e04141; 
        }
        #finalizar-btn-flotante::before { content: '✕'; color: white; font-size: 35px; font-weight: bold; }

        /* --- 5. LIMPIEZA TOTAL --- */
        [data-testid="stIconMaterial"], .st-emotion-cache-1ae8k9u, span[data-testid="stWidgetLabel"] { 
            display: none !important; 
        }
        </style>
    """, unsafe_allow_html=True)