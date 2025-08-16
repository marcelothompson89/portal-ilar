import streamlit as st
import os
import subprocess
import sys
from pathlib import Path

# Configuración de la página
st.set_page_config(
    page_title="Portal ILAR - Dashboards",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def main():
    """Aplicación principal para servir los dashboards"""
    
    # Verificar si hay parámetros de URL para determinar qué dashboard mostrar
    query_params = st.experimental_get_query_params()
    dashboard_type = query_params.get('dashboard', ['home'])[0]
    
    if dashboard_type == 'moleculas':
        show_moleculas_dashboard()
    elif dashboard_type == 'suplementos':
        show_suplementos_dashboard()
    else:
        show_redirect_message()

def show_redirect_message():
    """Muestra mensaje de redirección desde el portal web"""
    st.markdown("""
    <div style="text-align: center; padding: 4rem;">
        <h1>🧬 Portal ILAR - Dashboards</h1>
        <p style="font-size: 1.2rem; color: #666;">
            Para acceder a los dashboards, por favor utiliza el portal web:
        </p>
        <a href="login.html" target="_blank" style="
            display: inline-block;
            background: linear-gradient(135deg, #8BC34A 0%, #689F38 100%);
            color: white;
            padding: 1rem 2rem;
            text-decoration: none;
            border-radius: 10px;
            font-weight: bold;
            margin-top: 2rem;
        ">
            🔐 Acceder al Portal
        </a>
        
        <div style="margin-top: 3rem; padding: 2rem; background: #f8f9fa; border-radius: 10px;">
            <h3>📊 Dashboards Disponibles:</h3>
            <ul style="list-style: none; padding: 0;">
                <li style="margin: 1rem 0;">
                    <strong>🧪 Dashboard de Moléculas:</strong> Análisis de moléculas OTC
                </li>
                <li style="margin: 1rem 0;">
                    <strong>📊 Dashboard de Suplementos:</strong> Regulación en América Latina
                </li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)

def show_moleculas_dashboard():
    """Ejecuta el dashboard de moléculas"""
    try:
        # Verificar si el archivo existe
        if os.path.exists('dashboard_moleculas.py'):
            # Ejecutar el código del dashboard
            exec(open('dashboard_moleculas.py').read())
        else:
            show_placeholder_moleculas()
    except Exception as e:
        st.error(f"Error cargando dashboard de moléculas: {e}")
        show_placeholder_moleculas()

def show_suplementos_dashboard():
    """Ejecuta el dashboard de suplementos"""
    try:
        # Verificar si el archivo existe
        if os.path.exists('dashboard_suplementos.py'):
            # Ejecutar el código del dashboard
            exec(open('dashboard_suplementos.py').read())
        else:
            show_placeholder_suplementos()
    except Exception as e:
        st.error(f"Error cargando dashboard de suplementos: {e}")
        show_placeholder_suplementos()

def show_placeholder_moleculas():
    """Placeholder para dashboard de moléculas"""
    st.title("🧪 Dashboard de Moléculas ILAR")
    st.info("Dashboard de moléculas no encontrado. Coloca tu archivo como 'dashboard_moleculas.py'")
    
    # Mostrar datos de ejemplo
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Moléculas", "1,247")
    with col2:
        st.metric("Países", "15")
    with col3:
        st.metric("Categorías", "8")

def show_placeholder_suplementos():
    """Placeholder para dashboard de suplementos"""
    st.title("📊 Dashboard Suplementos América Latina")
    st.info("Dashboard de suplementos no encontrado. Coloca tu archivo como 'dashboard_suplementos.py'")
    
    # Mostrar datos de ejemplo
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Países", "16")
    with col2:
        st.metric("Ingredientes", "156")
    with col3:
        st.metric("Regulaciones", "12")

if __name__ == "__main__":
    main()