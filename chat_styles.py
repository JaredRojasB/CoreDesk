import streamlit as st

def aplicar_chat(): 
    st.markdown("""
        <style>
        /* --- 1. CABECERA Y LOGO --- */
        .header-fixed {
            position: fixed; top: 0; left: 0; width: 100%; height: 75px;
            background: white; z-index: 999; display: flex;
            align-items: center; padding: 0 5%; border-bottom: 1px solid #EEE;
        }
        .logo-chat { max-height: 55px; width: auto; }

        /* --- 2. TARJETA DE USUARIO CON CONTADOR --- */
        .user-card-formal {
            background-color: #ffffff; padding: 15px 25px;
            border-radius: 12px; box-shadow: 0px 4px 15px rgba(0,0,0,0.05);
            border-left: 5px solid #0E3255; margin-bottom: 25px;
            display: flex; justify-content: space-between; align-items: center;
            margin-top: 20px;
        }

        /* --- 3. BARRA DE CHAT Y BOTÓN "+" (CLIP) --- */
        /* Ajuste para que el texto no se encime con el icono */
        div[data-testid="stChatInput"] textarea {
            padding-right: 55px !important; 
        }
        
        /* Posicionamos el popover (+) a la DERECHA, junto a la flecha de enviar */
        .stPopover {
            position: fixed !important;
            bottom: 38px !important;
            right: calc(10% + 60px) !important; /* Ajustado para estar al lado de la flecha */
            z-index: 1001 !important;
        }
        .stPopover button { 
            background: #f0f2f6 !important; 
            color: #0E3255 !important; 
            border-radius: 50% !important;
            border: none !important;
            font-size: 20px !important;
            width: 35px !important;
            height: 35px !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
        }

        /* --- 4. COLORES DE BURBUJAS (Identidad CoreDesk) --- */
        /* Usuario (Azul CoreDesk) */
        [data-testid="stChatMessage"]:not([data-testid="stChatMessageAssistant"]) {
            background-color: #0E3255 !important;
            color: white !important;
            border-radius: 15px 15px 0px 15px !important;
        }
        /* Bot (Gris claro) */
        [data-testid="stChatMessageAssistant"] {
            background-color: #f1f3f5 !important;
            border-radius: 15px 15px 15px 0px !important;
        }

        /* --- 5. BOTÓN X FLOTANTE ROJO --- */
        #finalizar-btn-flotante {
            position: fixed; bottom: 40px; left: 40px;
            width: 65px; height: 65px; background-color: #FF4B4B;
            border-radius: 50%; display: flex; align-items: center;
            justify-content: center; box-shadow: 0px 5px 15px rgba(255, 75, 75, 0.4);
            cursor: pointer; z-index: 1002; transition: 0.3s ease;
            text-decoration: none; border: none;
        }
        #finalizar-btn-flotante:hover { transform: scale(1.1) rotate(90deg); background-color: #e04141; }
        #finalizar-btn-flotante::before { content: '✕'; color: white; font-size: 30px; font-weight: bold; }
        
        #finalizar-btn-flotante:hover::after {
            content: 'Finalizar chat'; position: absolute; left: 80px;
            background-color: #333; color: white; padding: 5px 12px;
            border-radius: 5px; font-size: 14px; white-space: nowrap;
        }

        /* --- 6. ELIMINAR ICONOS NARANJAS --- */
        [data-testid="stIconMaterial"], .st-emotion-cache-1ae8k9u, span[data-testid="stWidgetLabel"] { 
            display: none !important; 
        }
        </style>
    """, unsafe_allow_html=True)