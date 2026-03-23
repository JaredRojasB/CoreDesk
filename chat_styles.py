import streamlit as st

def aplicar_chat():
    st.markdown("""
        <style>
        /* Fondo de Chat Independiente */
        .stApp { background-color: #FFFFFF; } 

        /* LIMPIEZA TOTAL DE ICONOS (Evita el smart_toy y expand_more) */
        [data-testid="stIconMaterial"], span[data-testid="stWidgetLabel"], .st-emotion-cache-1ae8k9u { 
            display: none !important; 
        }

        /* CABECERA (Logo Izq y Contador Der) */
        .header-fixed {
            position: fixed; top: 0; left: 0; width: 100%; height: 70px;
            background: white; z-index: 1000; display: flex;
            align-items: center; justify-content: space-between;
            padding: 0 5%; border-bottom: 1px solid #EEE;
        }

        /* TARJETA DE USUARIO FORMAL */
        .main { padding-top: 80px; } /* Espacio para el header */
        .user-card {
            background: white; padding: 20px; border-radius: 12px;
            border-left: 6px solid #0E3255; box-shadow: 0 4px 15px rgba(0,0,0,0.05);
            margin-bottom: 20px;
        }

        /* BARRA DE CHAT FIJA CON CLIP INTEGRADO */
        div[data-testid="stChatInput"] {
            position: fixed !important; bottom: 30px !important;
            width: 80% !important; left: 50% !important;
            transform: translateX(-50%) !important;
            padding-left: 50px !important; 
            z-index: 998;
        }
        
        .stPopover {
            position: fixed !important; bottom: 42px !important;
            left: calc(10% + 20px) !important; z-index: 999 !important;
        }
        .stPopover button { background: transparent !important; color: #0E3255 !important; border: none !important; }

        /* BOTÓN X FLOTANTE (Inferior Izquierda) */
        #btn-exit {
            position: fixed; bottom: 40px; left: 40px;
            width: 65px; height: 65px; background: #FF4B4B;
            border-radius: 50%; display: flex; align-items: center;
            justify-content: center; color: white; font-size: 35px;
            text-decoration: none; z-index: 1001;
            box-shadow: 0 4px 15px rgba(255, 75, 75, 0.4);
            transition: 0.3s ease;
        }
        #btn-exit:hover { transform: scale(1.1) rotate(90deg); background: #E04141; }
        #btn-exit:hover::after {
            content: 'Finalizar chat'; position: absolute; left: 80px;
            background: #333; color: white; padding: 5px 12px;
            border-radius: 5px; font-size: 14px; white-space: nowrap;
        }
        </style>
    """, unsafe_allow_html=True)