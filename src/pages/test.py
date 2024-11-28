import streamlit as st

# Configuration du style
st.markdown("""
    <style>
    .metric-container {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: transform 0.3s ease;
    }
    .metric-container:hover {
        transform: scale(1.02);
    }
    .metric-label {
        color: #555;
        font-weight: 600;
        margin-bottom: 5px;
    }
    .metric-value {
        font-size: 24px;
        color: #1e3a8a;
        font-weight: bold;
    }
    .metric-delta {
        font-size: 16px;
        margin-top: 5px;
    }
    .positive-delta {
        color: green;
    }
    .negative-delta {
        color: red;
    }
    </style>
""", unsafe_allow_html=True)

# Widgets pour saisir dynamiquement les valeurs
st.header("Paramètres Météo")

col_temp, col_hum, col_press = st.columns(3)

with col_temp:
    temperature = st.number_input("Température (°C)", value=25.0, step=0.1)
    temp_delta = st.number_input("Variation Température", value=2.0, step=0.1)

with col_hum:
    humidite = st.number_input("Humidité (%)", value=60.0, step=0.1)
    hum_delta = st.number_input("Variation Humidité", value=-5.0, step=0.1)

with col_press:
    pression = st.number_input("Pression (hPa)", value=1013.0, step=0.1)
    press_delta = st.number_input("Variation Pression", value=0.0, step=0.1)

# Affichage des metrics
st.header("Tableau de Bord")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
    <div class="metric-container">
        <div class="metric-label">Température</div>
        <div class="metric-value">{temperature}°C</div>
        <div class="metric-delta {'positive-delta' if temp_delta >= 0 else 'negative-delta'}">
            {"↑" if temp_delta >= 0 else "↓"} {abs(temp_delta)}°C
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-container">
        <div class="metric-label">Humidité</div>
        <div class="metric-value">{humidite}%</div>
        <div class="metric-delta {'positive-delta' if hum_delta >= 0 else 'negative-delta'}">
            {"↑" if hum_delta >= 0 else "↓"} {abs(hum_delta)}%
        </div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-container">
        <div class="metric-label">Pression</div>
        <div class="metric-value">{pression} hPa</div>
        <div class="metric-delta {'positive-delta' if press_delta > 0 else 'negative-delta' if press_delta < 0 else ''}">
            {"↑" if press_delta > 0 else "↓" if press_delta < 0 else "Stable"}
            {" " + str(abs(press_delta)) if press_delta != 0 else ""}
        </div>
    </div>
    """, unsafe_allow_html=True)
