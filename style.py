# style.py
import streamlit as st

def apply_custom_styles():
    """Aplica el diseño Oasis con fondo de huella sutil (watermark)"""
    
    # URL DE TU IMAGEN DE HUELLA GRIS PÁLIDO Y TRANSPARENTE
    # Ejemplo: URL_HUELLA_SUTIL = "https://tu-hosting.com/huella_gris.png"
    URL_HUELLA_SUTIL = "URL_HUELLA = "https://raw.githubusercontent.com/Prototipo12bs/VeterinaraSPweb/main/huella.png"" 
    
    st.markdown(f"""
        <style>
        /* 1. Fondo de Marca de Agua: Huella sutil y repetida al fondo */
        [data-testid="stAppViewContainer"] {{
            background-image: url('{URL_HUELLA_SUTIL}') !important;
            background-repeat: repeat !important; /* Mosaico sutil */
            background-size: 150px !important;    /* Tamaño de la huella */
            background-attachment: fixed !important;
        }}
        
        /* Capa de suavizado para que el fondo sea Oasis Bone y no canse la vista */
        [data-testid="stAppViewContainer"]::before {{
            content: "";
            position: absolute;
            top: 0; left: 0; width: 100%; height: 100%;
            background-color: rgba(244, 247, 240, 0.9); /* Verde-Gris Oasis casi opaco */
            z-index: -1;
        }}

        /* 2. Tarjetas Blancas Súper Redondeadas (Para que resalten del fondo) */
        .header-box {{
            background-color: white;
            padding: 30px;
            border-radius: 30px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.03);
            margin-bottom: 25px;
            border: 1px solid #E9EDDF;
            text-align: center;
        }}

        div[data-testid="stMetric"] {{
            background-color: white !important;
            border-radius: 25px !important;
            padding: 20px !important;
            border: 1px solid #E9EDDF !important;
            box-shadow: 0 4px 12px rgba(0,0,0,0.02) !important;
        }}
        
        /* Títulos de Métricas en Gris Oscuro OASIS */
        div[data-testid="stMetricLabel"] > div > p {{
            color: #2D3436 !important;
            font-weight: 600 !important;
        }}

        /* 3. Pestañas (Tabs) Estilo Cápsula (Drink tracker style) */
        .stTabs [data-baseweb="tab-list"] {
            gap: 12px !important;
        }

        .stTabs [data-baseweb="tab"] {
            background-color: rgba(255, 255, 255, 0.8) !important;
            border-radius: 50px !important;
            color: #636E72 !important;
            border: 1px solid #E9EDDF !important;
            padding: 8px 25px !important;
        }

        .stTabs [data-baseweb="tab"][aria-selected="true"] {
            background-color: #95C06A !important;
            color: white !important;
        }

        /* 4. Asegurar legibilidad en Dataframes */
        [data-testid="stDataFrame"], .stDataFrame {
            background-color: white !important;
            border-radius: 20px !important;
            padding: 10px;
        }
        </style>
        """, unsafe_allow_html=True)

def render_header(user_name):
    """Banner principal minimalista"""
    st.markdown(f"""
        <div class="header-box">
            <h1 style='margin:0; color:#2D3436; font-size: 1.8rem; font-weight:700;'>
                🐾 OASIS <span style='color:#95C06A; font-weight: 300;'>PET TRACKER</span>
            </h1>
            <p style='color:#636E72;'>Bienvenido | Sesión: <b>{user_name}</b></p>
        </div>
        """, unsafe_allow_html=True)
