import streamlit as st

def aplicar_estilos_chat():
    st.markdown("""
        <style>
        /* --- 1. TARJETA DE USUARIO FORMAL CON CONTADOR --- */
        .user-card-formal {
            background-color: #ffffff; padding: 15px 25px;
            border-radius: 12px; box-shadow: 0px 4px 15px rgba(0,0,0,0.05);
            border-left: 5px solid #0E3255; margin-bottom: 25px;
            display: flex; justify-content: space-between; align-items: center;
        }

        /* --- 2. CLIP INTEGRADO EN LA BARRA (A la izquierda) --- */
        /* Ajustamos el padding del input para que el texto no tape al clip */
        div[data-testid="stChatInput"] textarea {
            padding-left: 50px !important;
        }
        
        /* Posicionamos el clip (popover) exactamente sobre la barra */
        .stPopover {
            position: fixed !important;
            bottom: 42px !important; /* Altura de la barra */
            left: calc(10% + 25px) !important; /* Alineado al inicio del input */
            z-index: 1001 !important;
        }
        .stPopover button { background: transparent !important; color: #0E3255 !important; border: none !important; }

        /* --- 3. BOTÓN FLOTANTE 'X' (Inferior Izquierda) --- */
        #finalizar-btn-flotante {
            position: fixed; bottom: 40px; left: 40px;
            width: 70px; height: 70px; background-color: #FF4B4B;
            border-radius: 50%; display: flex; align-items: center;
            justify-content: center; box-shadow: 0px 5px 15px rgba(255, 75, 75, 0.4);
            cursor: pointer; z-index: 1001; transition: 0.3s ease;
            text-decoration: none; border: none;
        }
        #finalizar-btn-flotante:hover { transform: scale(1.1) rotate(90deg); background-color: #e04141; }
        
        /* Leyenda al pasar el mouse */
        #finalizar-btn-flotante:hover::after {
            content: 'Finalizar chat'; position: absolute; left: 85px;
            background-color: #333; color: white; padding: 5px 12px;
            border-radius: 5px; font-size: 14px; white-space: nowrap;
        }

        /* --- 4. FIX ICONOS NARANJAS --- */
        [data-testid="stIconMaterial"], .st-emotion-cache-1ae8k9u, span[data-testid="stWidgetLabel"] { 
            display: none !important; 
        }
        </style>
    """, unsafe_allow_html=True)