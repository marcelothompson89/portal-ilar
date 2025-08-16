import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Configuración de la página
st.set_page_config(
    page_title="Dashboard de Moléculas ILAR",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Título principal
st.title("Dashboard de Moléculas ILAR")
st.markdown("---")

# Función para cargar datos
@st.cache_data
def load_data():
    # Reemplaza esta ruta con la ruta a tu archivo Excel
    df = pd.read_excel('Version final Extracto base de datos Mar 2023.xlsx', sheet_name='Base en inglés')
    return df

# Función para limpiar duplicados
def clean_duplicates(df):
    """
    Limpia duplicados basándose en columnas clave para evitar repeticiones
    """
    # Definir columnas clave para identificar duplicados
    key_columns = ['Molecule', 'Country', 'Switch Year', 'Strength']
    
    # Eliminar duplicados exactos en todas las columnas
    df_cleaned = df.drop_duplicates()
    
    # Eliminar duplicados basándose en las columnas clave
    # Mantener el primer registro de cada combinación única
    df_cleaned = df_cleaned.drop_duplicates(subset=key_columns, keep='first')
    
    return df_cleaned

# Cargar datos
try:
    df = load_data()
    
    # Limpiar duplicados
    df = clean_duplicates(df)
    
    # Leyenda explicativa sobre tipos de medicamentos
    st.info("""
    **ℹ️ Información sobre tipos de medicamentos:**
    - **OTC** (Venta libre): Medicamentos que se pueden comprar sin receta médica
    - **Rx** (Solo prescripción): Medicamentos que requieren receta médica
    - **Rx-OTC**: Moléculas o combinaciones que pueden estar en ambas categorías dependiendo de la dosis
    """)
    
    # FILTROS PRINCIPALES EN LA PARTE FRONTAL
    st.header("🔍 Filtros de Búsqueda")
    
    # Crear dos columnas para los filtros principales
    col_filter1, col_filter2 = st.columns(2)
    
    with col_filter1:
        # Filtro de molécula con búsqueda
        molecules = sorted(df['Molecule'].unique())
        selected_molecule = st.selectbox(
            "**Selecciona una molécula:**",
            options=["Todas las moléculas"] + molecules,
            help="Busca y selecciona una molécula específica"
        )
    
    with col_filter2:
        # Filtro de países
        countries = sorted(df['Country'].unique())
        selected_countries = st.multiselect(
            "**Selecciona países:**",
            options=countries,
            default=[],  # Sin países seleccionados por defecto
            help="Selecciona uno o más países para analizar (vacío = todos los países)"
        )
    
    # Aplicar filtros
    filtered_df = df.copy()
    
    # Filtrar por molécula si se seleccionó una específica
    if selected_molecule != "Todas las moléculas":
        filtered_df = filtered_df[filtered_df['Molecule'] == selected_molecule]
    
    # Aplicar filtro de países
    if selected_countries:
        filtered_df = filtered_df[filtered_df['Country'].isin(selected_countries)]
    
    st.markdown("---")
    
    # Mostrar información general
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total de registros", len(filtered_df))
    
    with col2:
        st.metric("Países únicos", filtered_df['Country'].nunique())
    
    with col3:
        st.metric("Moléculas únicas", filtered_df['Molecule'].nunique())
    
    st.markdown("---")
    

    
    # Crear tabs para diferentes visualizaciones
    tab1, tab2 = st.tabs(["📋 Datos", "📊 Análisis por País"])
    
    with tab1:
        st.header("Datos Filtrados")
        
        # Mostrar el dataframe filtrado
        st.write(f"Mostrando {len(filtered_df)} registros:")
        
        # Selectbox para elegir qué columnas mostrar
        all_columns = filtered_df.columns.tolist()
        selected_columns = st.multiselect(
            "Selecciona columnas a mostrar:",
            options=all_columns,
            default=['Molecule', 'Switch Year', 'Country', 'RX-OTC - Product', 'Strength', 'NFC1']
        )
        
        if selected_columns:
            display_df = filtered_df[selected_columns]
            st.dataframe(display_df, use_container_width=True)
        else:
            st.warning("Selecciona al menos una columna para mostrar los datos.")
    
    with tab2:
        st.header("Análisis por País")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Gráfico de barras - Moléculas por país
            country_molecules = filtered_df.groupby('Country')['Molecule'].nunique().sort_values(ascending=False).head(15)
            fig_bar = px.bar(
                x=country_molecules.index,
                y=country_molecules.values,
                title="Número de moléculas por país",
                labels={'x': 'País', 'y': 'Número de moléculas'},
                color=country_molecules.values,
                color_continuous_scale="viridis"
            )
            fig_bar.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig_bar, use_container_width=True)
        
        with col2:
            # Gráfico de pie - Distribución RX vs OTC
            if 'RX-OTC - Molecule' in filtered_df.columns:
                rx_otc_counts = filtered_df['RX-OTC - Molecule'].value_counts()
                fig_pie = px.pie(
                    values=rx_otc_counts.values,
                    names=rx_otc_counts.index,
                    title="Distribución RX vs OTC"
                )
                st.plotly_chart(fig_pie, use_container_width=True)

except FileNotFoundError:
    st.error("⚠️ No se pudo encontrar el archivo Excel. Por favor, asegúrate de que el archivo 'Version final Extracto base de datos Mar 2023.xlsx' esté en el mismo directorio que este script.")
    st.info("Puedes subir el archivo usando el widget de carga de archivos de Streamlit o ajustar la ruta en el código.")
except Exception as e:
    st.error(f"Error al cargar los datos: {str(e)}")
    st.info("Verifica que el archivo Excel tenga el formato correcto y que la hoja 'Base en inglés' exista.")

# Footer
st.markdown("---")
st.markdown("💡 **Tip:** Usa los filtros principales en la parte superior para explorar los datos de manera intuitiva.")