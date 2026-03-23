import streamlit as st

def aplicar_chat():
    st.markdown("""
        <style>
        /* ==========================================
           1. HARD RESET VISUAL (FONDO BLANCO)
           ========================================== */
        .stApp { background-color: #FFFFFF; }
        div[data-testid="stHeader"], div[data-testid="stSidebarNav"] { display: none; }

        /* ==========================================
           2. LIMPIEZA TOTAL DE CAPAS DE CARGA (HACK)
           Este bloque elimina el 'mono' y la capa gris
           ========================================== */
        
        /* Oculta el icono cargando nativo (el 'mono') */
        [data-testid="stStatusWidget"] {
            display: none !important;
            visibility: hidden !important;
        }

        /* Oculta la capa gris que se pone encima al procesar */
        .st-emotion-cache-1ae8k9u, 
        .st-emotion-cache-p5m09v,
        div[data-test-id="stStatusWidgetOverlay"] {
            background-color: transparent !important;
            opacity: 0 !important;
            pointer-events: none !important;
        }

        /* ==========================================
           3. CABECERA FIJA PROFESIONAL
           ========================================== */
        .header-fixed {
            position: fixed; top: 0; left: 0; width: 100%; height: 75px;
            background: white; z-index: 1000; display: flex;
            align-items: center; padding: 0 5%; border-bottom: 1px solid #EEE;
            box-shadow: 0px 2px 10px rgba(0,0,0,0.03);
        }

        /* ==========================================
           4. TARJETA DE USUARIO FORMAL
           ========================================== */
        .user-card-pro {
            background-color: #ffffff; padding: 15px 25px;
            border-radius: 12px; box-shadow: 0px 4px 15px rgba(0,0,0,0.05);
            border-left: 6px solid #0E3255; margin-bottom: 25px;
            display: flex; justify-content: space-between; align-items: center;
            margin-top: 20px;
        }

        /* ==========================================
           5. MATAR ICONOS NARANJAS (smart_toy / expand_more)
           ========================================== */
        [data-testid="stIconMaterial"], .st-emotion-cache-1ae8k9u, span[data-testid="stWidgetLabel"] { 
            display: none !important; 
        }
        </style>
    """, unsafe_allow_html=True)