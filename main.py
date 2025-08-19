#!/usr/bin/env python3
"""
Portal ILAR - FastAPI + Plotly
Solución optimizada para producción en Render
Versión refactorizada con soporte completo para suplementos
"""

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from typing import List, Optional, Dict, Any
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.utils
import json
import os
import logging
import numpy as np
from pathlib import Path
import uvicorn
from contextlib import asynccontextmanager
from pandas.api.types import is_datetime64_any_dtype, is_datetime64tz_dtype
from fastapi.encoders import jsonable_encoder

# ==============================================
# CONFIGURACIÓN Y LOGGING
# ==============================================

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cache global para datos
data_cache = {}

# ==============================================
# FUNCIONES DE CARGA DE DATOS
# ==============================================

def load_regulatory_data():
    """Cargar datos regulatorios desde el archivo JSON"""
    try:
        regulatory_file = 'regulatory_data.json'
        if os.path.exists(regulatory_file):
            with open(regulatory_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            logger.warning(f"Archivo {regulatory_file} no encontrado, usando datos de ejemplo")
            return create_sample_regulatory_data()
    except Exception as e:
        logger.error(f"Error cargando datos regulatorios: {e}")
        return create_sample_regulatory_data()

def create_sample_regulatory_data():
    """Crear datos regulatorios de ejemplo"""
    return {
        "regulatory_data": {
            "Argentina": {
                "country_code": "AR",
                "sections": {
                    "instrumento_legal": {
                        "title": "Instrumento Legal",
                        "content": "Código Alimentario Argentino (CAA) y Resolución Conjunta 3/2020",
                        "type": "legal_framework"
                    },
                    "definicion_legal": {
                        "title": "Definición Legal",
                        "content": "Suplementos dietarios: productos destinados a incrementar la ingesta dietaria habitual",
                        "type": "definition"
                    },
                    "categoria_regulatoria": {
                        "title": "Categoría Regulatoria",
                        "content": "Alimento",
                        "type": "category",
                        "value": "Alimento"
                    },
                    "proceso_registro": {
                        "title": "Proceso de Registro",
                        "content": "Registro",
                        "type": "registration_type",
                        "value": "Registro"
                    },
                    "tiempo_aprobacion": {
                        "title": "Tiempo de Aprobación",
                        "content": "20 días hábiles (legislación) / 90-120 días (industria)",
                        "type": "timeline",
                        "legal_time": "20 días hábiles",
                        "industry_time": "90-120 días hábiles"
                    },
                    "propiedades_salud": {
                        "title": "Declaraciones de Salud",
                        "content": "No permitidas según Disposición 8095/2023",
                        "type": "health_claims",
                        "permitted": False
                    }
                }
            },
            "Brasil": {
                "country_code": "BR",
                "sections": {
                    "instrumento_legal": {
                        "title": "Instrumento Legal",
                        "content": "RDC N° 243/2018 e IN N° 28/2018",
                        "type": "legal_framework"
                    },
                    "definicion_legal": {
                        "title": "Definición Legal",
                        "content": "Suplemento alimentario: produto de ingestão oral em formas farmacêuticas",
                        "type": "definition"
                    },
                    "categoria_regulatoria": {
                        "title": "Categoría Regulatoria",
                        "content": "Alimento",
                        "type": "category",
                        "value": "Alimento"
                    },
                    "proceso_registro": {
                        "title": "Proceso de Registro",
                        "content": "Notificación o Registro (según contenga enzimas/probióticos)",
                        "type": "registration_type",
                        "value": "Notificación/Registro"
                    },
                    "tiempo_aprobacion": {
                        "title": "Tiempo de Aprobación",
                        "content": "60 días (legislación) / 90-120 días (industria)",
                        "type": "timeline",
                        "legal_time": "60 días",
                        "industry_time": "90-120 días"
                    },
                    "propiedades_salud": {
                        "title": "Declaraciones de Salud",
                        "content": "Permitidas según lista positiva de IN 28/2018",
                        "type": "health_claims",
                        "permitted": True
                    }
                }
            }
        }
    }

# Cargar datos regulatorios al inicio
regulatory_data = load_regulatory_data()

def cargar_datos_suplementos():
    """Carga los datos de suplementos desde los archivos CSV"""
    try:
        # Cargar datos principales
        df_principal = pd.read_csv('suplementos_normalizados_completo.csv', dtype={'referencias': 'str'})
        
        # Cargar referencias
        df_ref_vitaminas = pd.read_csv('referencias_suplementos_vitaminas.csv', dtype={'referencia': 'str'})
        df_ref_minerales = pd.read_csv('referencias_suplementos_minerales.csv', dtype={'referencia': 'str'})
        
        df_referencias = pd.concat([df_ref_vitaminas, df_ref_minerales], ignore_index=True)
        
        # Limpiar valores 'nan' en las referencias
        df_principal['referencias'] = df_principal['referencias'].replace('nan', pd.NA)
        
        return df_principal, df_referencias
    except FileNotFoundError as e:
        logger.warning(f"Error al cargar archivos de suplementos: {e}")
        return create_sample_supplements_data(), create_sample_references_data()

def create_sample_supplements_data():
    """Crear datos de ejemplo para suplementos"""
    countries = ['Argentina', 'Brasil', 'Chile', 'Colombia', 'Costa Rica', 'México', 'Perú']
    ingredients = ['Vitamina C', 'Vitamina D', 'Vitamina B12', 'Ácido Fólico', 'Hierro', 'Calcio', 'Zinc', 'Omega 3']
    types = ['Vitamina', 'Vitamina', 'Vitamina', 'Vitamina', 'Mineral', 'Mineral', 'Mineral', 'Ácido Graso']
    
    data = []
    for country in countries:
        for i, ingredient in enumerate(ingredients):
            data.append({
                'pais': country,
                'ingrediente': ingredient,
                'tipo': types[i],
                'minimo': np.random.uniform(10, 100),
                'maximo': np.random.uniform(100, 1000),
                'unidad': 'mg' if types[i] != 'Vitamina' or 'D' in ingredient else 'μg',
                'establecido': np.random.choice([True, False], p=[0.8, 0.2]),
                'categoria_regulacion': np.random.choice(['Alimento', 'Suplemento', 'Medicamento'], p=[0.5, 0.4, 0.1]),
                'referencias': f'REF{np.random.randint(1, 20)}',
                'valor_original': f'{np.random.uniform(50, 500):.1f}'
            })
    
    return pd.DataFrame(data)

def create_sample_references_data():
    """Crear datos de ejemplo para referencias"""
    data = []
    for i in range(1, 21):
        data.append({
            'referencia': f'REF{i}',
            'tipo': np.random.choice(['Vitamina', 'Mineral']),
            'descripcion': f'Descripción de referencia {i} - Regulación específica para el ingrediente'
        })
    
    return pd.DataFrame(data)

async def load_moleculas_data():
    """Cargar datos de moléculas"""
    try:
        excel_file = 'Version final Extracto base de datos Mar 2023.xlsx'
        if not os.path.exists(excel_file):
            logger.warning(f"❌ Archivo {excel_file} no encontrado")
            data_cache['moleculas'] = pd.DataFrame()
            return
            
        logger.info(f"📂 Cargando archivo: {excel_file}")
        
        # Cargar datos de moléculas
        df_moleculas = pd.read_excel(excel_file, sheet_name='Base en inglés')
        
        # Limpiar duplicados
        key_columns = ['Molecule', 'Country', 'Switch Year', 'Strength']
        df_moleculas = df_moleculas.drop_duplicates()
        df_moleculas = df_moleculas.drop_duplicates(subset=key_columns, keep='first')
        
        # Normalizar columnas de texto
        for col in ['Molecule', 'Country', 'RX-OTC - Molecule', 'RX-OTC - Product', 'Strength']:
            if col in df_moleculas.columns:
                df_moleculas[col] = df_moleculas[col].astype(str).str.strip()

        # Coerción segura del año
        if 'Switch Year' in df_moleculas.columns:
            df_moleculas['Switch Year'] = (
                df_moleculas['Switch Year']
                .replace({'-': None, '—': None, '': None})
            )
            df_moleculas['Switch Year'] = pd.to_numeric(df_moleculas['Switch Year'], errors='coerce')

        data_cache['moleculas'] = df_moleculas
        logger.info(f"✅ Moléculas cargadas: {len(df_moleculas)} registros")
        
    except Exception as e:
        logger.error(f"❌ Error cargando moléculas: {e}")
        data_cache['moleculas'] = pd.DataFrame()

async def load_supplements_data():
    """Cargar datos de suplementos"""
    try:
        logger.info("📊 Cargando datos de suplementos...")
        
        # Verificar si los archivos existen
        files_needed = [
            'suplementos_normalizados_completo.csv',
            'referencias_suplementos_vitaminas.csv', 
            'referencias_suplementos_minerales.csv'
        ]
        
        missing_files = [f for f in files_needed if not os.path.exists(f)]
        if missing_files:
            logger.warning(f"❌ Archivos de suplementos no encontrados: {missing_files}")
            logger.info("🔄 Usando datos de ejemplo...")
        
        # Cargar datos (reales o de ejemplo)
        df_principal, df_referencias = cargar_datos_suplementos()
        
        data_cache['suplementos_principal'] = df_principal
        data_cache['suplementos_referencias'] = df_referencias
        
        logger.info(f"✅ Suplementos cargados: {len(df_principal)} registros principales, {len(df_referencias)} referencias")
        
    except Exception as e:
        logger.error(f"❌ Error cargando datos de suplementos: {e}")
        data_cache['suplementos_principal'] = create_sample_supplements_data()
        data_cache['suplementos_referencias'] = create_sample_references_data()

async def load_data_on_startup():
    """Cargar todos los datos al iniciar la aplicación"""
    logger.info("🔄 Cargando datos en memoria...")
    
    # Cargar datos de moléculas
    await load_moleculas_data()
    
    # Cargar datos de suplementos
    await load_supplements_data()

# ==============================================
# CONFIGURACIÓN DE LA APLICACIÓN
# ==============================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestión del ciclo de vida de la aplicación"""
    # Startup
    await load_data_on_startup()
    yield
    # Shutdown
    logger.info("🛑 Cerrando aplicación...")

# Crear aplicación FastAPI
app = FastAPI(
    title="Portal ILAR API",
    description="API para dashboards de regulación farmacéutica en América Latina",
    version="2.0.0",
    lifespan=lifespan
)

# Configurar templates y archivos estáticos
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# ==============================================
# RUTAS PRINCIPALES
# ==============================================

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Página de inicio"""
    if os.path.exists('loading_temp.html'):
        with open('loading_temp.html', 'r', encoding='utf-8') as f:
            content = f.read()
        return HTMLResponse(content=content)
    else:
        return templates.TemplateResponse("login.html", {"request": request})

@app.get("/loading", response_class=HTMLResponse)
async def loading_page(request: Request):
    """Página de carga standalone"""
    if os.path.exists('loading_temp.html'):
        with open('loading_temp.html', 'r', encoding='utf-8') as f:
            content = f.read()
        return HTMLResponse(content=content)
    else:
        return templates.TemplateResponse("login.html", {"request": request})

@app.get("/login.html", response_class=HTMLResponse)
async def login_page(request: Request):
    """Página de login"""
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/dashboard.html", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    """Página principal del portal"""
    return templates.TemplateResponse("dashboard.html", {"request": request})

# ==============================================
# DASHBOARDS INTEGRADOS
# ==============================================

@app.get("/analytics/molecular-data", response_class=HTMLResponse)
async def dashboard_moleculas(request: Request):
    """Dashboard de moléculas"""
    return templates.TemplateResponse("dashboard_moleculas.html", {"request": request})

@app.get("/analytics/supplement-regulations", response_class=HTMLResponse)
async def dashboard_suplementos(request: Request):
    """Dashboard de suplementos"""
    return templates.TemplateResponse("dashboard_suplementos.html", {"request": request})

# ==============================================
# UTILIDADES PARA APIS
# ==============================================

def make_json_safe(df: pd.DataFrame) -> pd.DataFrame:
    """Convierte un DataFrame en JSON-safe reemplazando NaN/Inf/NaT"""
    df_safe = df.copy()
    
    # Convertir fechas a string ISO
    for col in df_safe.columns:
        if is_datetime64_any_dtype(df_safe[col]) or is_datetime64tz_dtype(df_safe[col]):
            df_safe[col] = pd.to_datetime(df_safe[col], errors="coerce").dt.strftime("%Y-%m-%d")
    
    # Reemplazar NaN/Inf por None
    df_safe = df_safe.replace([pd.NA, pd.NaT, np.nan, np.inf, -np.inf], None)
    df_safe = df_safe.where(pd.notna(df_safe), None)
    
    return df_safe

# ==============================================
# APIs DE MOLÉCULAS
# ==============================================

@app.get("/api/moleculas/stats")
async def get_moleculas_stats(
    molecule: Optional[str] = Query(None, description="Filtrar por molécula específica"),
    countries: Optional[List[str]] = Query(None, description="Lista de países a incluir")
):
    """Obtener estadísticas básicas de moléculas"""
    
    df = data_cache.get('moleculas')
    if df is None or df.empty:
        raise HTTPException(status_code=500, detail="Datos de moléculas no disponibles")
    
    # Aplicar filtros
    filtered_df = df.copy()
    if molecule and molecule != "all":
        filtered_df = filtered_df[filtered_df['Molecule'] == molecule]
    if countries:
        filtered_df = filtered_df[filtered_df['Country'].isin(countries)]

    # Calcular rango de años
    min_year = None
    max_year = None
    if 'Switch Year' in df.columns:
        yy = pd.to_numeric(df['Switch Year'], errors='coerce').dropna()
        if not yy.empty:
            min_year = int(yy.min())
            max_year = int(yy.max())
    
    return {
        "total_records": len(filtered_df),
        "unique_countries": filtered_df['Country'].nunique(),
        "unique_molecules": filtered_df['Molecule'].nunique(),
        "available_molecules": sorted(df['Molecule'].dropna().astype(str).unique().tolist()),
        "available_countries": sorted(df['Country'].dropna().astype(str).unique().tolist()),
        "date_range": {"min_year": min_year, "max_year": max_year}
    }

@app.get("/api/moleculas/data")
async def get_moleculas_data(
    molecule: Optional[str] = Query(None),
    countries: Optional[List[str]] = Query(None),
    limit: int = Query(50, ge=1, le=1000, description="Número máximo de registros"),
    offset: int = Query(0, ge=0, description="Offset para paginación")
):
    """Obtener datos de moléculas con paginación"""
    df = data_cache.get('moleculas')
    if df is None or df.empty:
        raise HTTPException(status_code=500, detail="Datos de moléculas no disponibles")

    # Aplicar filtros
    filtered_df = df.copy()
    if molecule and molecule != "all":
        filtered_df = filtered_df[filtered_df['Molecule'] == molecule]
    if countries and len(countries) > 0:
        filtered_df = filtered_df[filtered_df['Country'].isin(countries)]

    total_records = len(filtered_df)
    paginated_df = filtered_df.iloc[offset:offset + limit].copy()

    # Hacer JSON-safe
    paginated_df = make_json_safe(paginated_df)

    payload = {
        "data": paginated_df.to_dict("records"),
        "pagination": {
            "total": total_records,
            "limit": limit,
            "offset": offset,
            "has_next": offset + limit < total_records
        }
    }

    return JSONResponse(content=jsonable_encoder(payload))

@app.get("/api/moleculas/charts")
async def get_moleculas_charts(
    molecule: Optional[str] = Query(None),
    countries: Optional[List[str]] = Query(None)
):
    """Generar gráficos para el dashboard de moléculas"""
    
    df = data_cache.get('moleculas')
    if df is None or df.empty:
        raise HTTPException(status_code=500, detail="Datos de moléculas no disponibles")
    
    # Aplicar filtros
    filtered_df = df.copy()
    if molecule and molecule != "all":
        filtered_df = filtered_df[filtered_df['Molecule'] == molecule]
    if countries and len(countries) > 0:
        filtered_df = filtered_df[filtered_df['Country'].isin(countries)]
    
    charts = {}
    
    try:
        # Gráfico 1: Moléculas únicas por país
        if {'Country', 'Molecule'}.issubset(filtered_df.columns) and not filtered_df.empty:
            country_molecules = (
                filtered_df.groupby('Country')['Molecule']
                .nunique()
                .sort_values(ascending=False)
                .head(15)
            )
            if not country_molecules.empty:
                fig_bar = px.bar(
                    x=country_molecules.index,
                    y=country_molecules.values,
                    title="Número de moléculas únicas por país",
                    labels={'x': 'País', 'y': 'Número de moléculas'},
                    color=country_molecules.values,
                    color_continuous_scale="viridis"
                )
                fig_bar.update_layout(
                    xaxis_tickangle=-45, 
                    height=400,
                    showlegend=False,
                    margin=dict(l=40, r=40, t=60, b=100),
                    xaxis_title="País",
                    yaxis_title="Número de moléculas"
                )
                charts['molecules_by_country'] = json.loads(json.dumps(fig_bar, cls=plotly.utils.PlotlyJSONEncoder))
        
        # Gráfico 2: Distribución RX vs OTC
        if 'RX-OTC - Molecule' in filtered_df.columns and not filtered_df.empty:
            rx_series = filtered_df['RX-OTC - Molecule'].astype(str).str.strip()
            rx_series = rx_series.replace({'': None, 'nan': None, 'None': None, 'NaN': None})
            rx_otc_counts = rx_series.dropna().value_counts()
            if not rx_otc_counts.empty:
                fig_pie = px.pie(
                    values=rx_otc_counts.values,
                    names=rx_otc_counts.index,
                    title="Distribución por tipo de regulación (RX-OTC)"
                )
                fig_pie.update_layout(height=400)
                charts['rx_otc_distribution'] = json.loads(json.dumps(fig_pie, cls=plotly.utils.PlotlyJSONEncoder))
        
        # Gráfico 3: Timeline de switches
        if 'Switch Year' in filtered_df.columns and not filtered_df.empty:
            yr = pd.to_numeric(filtered_df['Switch Year'], errors='coerce')
            yr_mask = yr.between(1990, 2030, inclusive='both')
            year_data = filtered_df.loc[yr_mask].copy()
            
            if not year_data.empty:
                year_data['Switch Year'] = yr.loc[yr_mask]
                year_counts = (year_data
                               .groupby('Switch Year', dropna=True)
                               .size()
                               .reset_index(name='count')
                               .sort_values('Switch Year'))
                
                if not year_counts.empty:
                    fig_timeline = px.line(
                        year_counts, 
                        x='Switch Year', 
                        y='count',
                        title="Evolución de switches por año",
                        markers=True
                    )
                    fig_timeline.update_layout(height=400)
                    charts['switches_timeline'] = json.loads(json.dumps(fig_timeline, cls=plotly.utils.PlotlyJSONEncoder))
        
        # Gráfico 4: Top moléculas
        if 'Molecule' in filtered_df.columns and not filtered_df.empty:
            top_molecules = filtered_df['Molecule'].value_counts().head(10)
            if not top_molecules.empty:
                fig_top = px.bar(
                    x=top_molecules.values,
                    y=top_molecules.index,
                    orientation='h',
                    title="Top 10 moléculas más frecuentes",
                    labels={'x': 'Número de registros', 'y': 'Molécula'}
                )
                fig_top.update_layout(
                    height=400, 
                    yaxis={'categoryorder': 'total ascending'},
                    margin=dict(l=150, r=40, t=60, b=40)
                )
                charts['top_molecules'] = json.loads(json.dumps(fig_top, cls=plotly.utils.PlotlyJSONEncoder))
        
    except Exception as e:
        logger.error(f"Error generando gráficos de moléculas: {e}")
        raise HTTPException(status_code=500, detail=f"Error generando gráficos: {str(e)}")
    
    return charts

# ==============================================
# APIs DE SUPLEMENTOS
# ==============================================

@app.get("/api/suplementos/stats")
async def get_suplementos_stats(
    ingredient: Optional[str] = Query(None, description="Filtrar por ingrediente específico"),
    countries: Optional[List[str]] = Query(None, description="Lista de países a incluir"),
    ingredient_type: Optional[str] = Query(None, description="Filtrar por tipo de ingrediente")
):
    """Obtener estadísticas básicas de suplementos"""
    
    df = data_cache.get('suplementos_principal')
    if df is None or df.empty:
        raise HTTPException(status_code=500, detail="Datos de suplementos no disponibles")
    
    # Aplicar filtros
    filtered_df = df.copy()
    if ingredient and ingredient != "all":
        filtered_df = filtered_df[filtered_df['ingrediente'] == ingredient]
    if countries:
        filtered_df = filtered_df[filtered_df['pais'].isin(countries)]
    if ingredient_type and ingredient_type != "all":
        filtered_df = filtered_df[filtered_df['tipo'] == ingredient_type]
    
    return {
        "total_records": len(filtered_df),
        "unique_countries": filtered_df['pais'].nunique(),
        "unique_ingredients": filtered_df['ingrediente'].nunique(),
        "unique_types": filtered_df['tipo'].nunique(),
        "available_ingredients": sorted(df['ingrediente'].dropna().unique().tolist()),
        "available_countries": sorted(df['pais'].dropna().unique().tolist()),
        "available_types": sorted(df['tipo'].dropna().unique().tolist()),
        "established_percentage": (filtered_df['establecido'].sum() / len(filtered_df) * 100) if len(filtered_df) > 0 else 0
    }

@app.get("/api/suplementos/data")
async def get_suplementos_data(
    ingredient: Optional[str] = Query(None),
    countries: Optional[List[str]] = Query(None),
    ingredient_type: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    """Obtener datos de suplementos con paginación"""
    df = data_cache.get('suplementos_principal')
    if df is None or df.empty:
        raise HTTPException(status_code=500, detail="Datos de suplementos no disponibles")

    # Aplicar filtros
    filtered_df = df.copy()
    if ingredient and ingredient != "all":
        filtered_df = filtered_df[filtered_df['ingrediente'] == ingredient]
    if countries and len(countries) > 0:
        filtered_df = filtered_df[filtered_df['pais'].isin(countries)]
    if ingredient_type and ingredient_type != "all":
        filtered_df = filtered_df[filtered_df['tipo'] == ingredient_type]

    total_records = len(filtered_df)
    paginated_df = filtered_df.iloc[offset:offset + limit].copy()

    # Hacer JSON-safe
    paginated_df = make_json_safe(paginated_df)

    payload = {
        "data": paginated_df.to_dict("records"),
        "pagination": {
            "total": total_records,
            "limit": limit,
            "offset": offset,
            "has_next": offset + limit < total_records
        }
    }

    return JSONResponse(content=jsonable_encoder(payload))

@app.get("/api/suplementos/charts")
async def get_suplementos_charts(
    ingredient: Optional[str] = Query(None),
    countries: Optional[List[str]] = Query(None),
    ingredient_type: Optional[str] = Query(None)
):
    """Generar gráficos para el dashboard de suplementos"""
    
    df = data_cache.get('suplementos_principal')
    if df is None or df.empty:
        raise HTTPException(status_code=500, detail="Datos de suplementos no disponibles")
    
    # Aplicar filtros
    filtered_df = df.copy()
    if ingredient and ingredient != "all":
        filtered_df = filtered_df[filtered_df['ingrediente'] == ingredient]
    if countries and len(countries) > 0:
        filtered_df = filtered_df[filtered_df['pais'].isin(countries)]
    if ingredient_type and ingredient_type != "all":
        filtered_df = filtered_df[filtered_df['tipo'] == ingredient_type]
    
    charts = {}
    
    try:
        # Gráfico 1: Ingredientes por país
        if not filtered_df.empty:
            country_ingredients = (
                filtered_df.groupby('pais')['ingrediente']
                .nunique()
                .sort_values(ascending=False)
                .head(15)
            )
            if not country_ingredients.empty:
                fig_bar = px.bar(
                    x=country_ingredients.index,
                    y=country_ingredients.values,
                    title="Número de ingredientes únicos por país",
                    labels={'x': 'País', 'y': 'Número de ingredientes'},
                    color=country_ingredients.values,
                    color_continuous_scale="viridis"
                )
                fig_bar.update_layout(xaxis_tickangle=-45, height=400, showlegend=False)
                charts['ingredients_by_country'] = json.loads(json.dumps(fig_bar, cls=plotly.utils.PlotlyJSONEncoder))
        
        # Gráfico 2: Distribución por tipo
        if not filtered_df.empty:
            type_counts = filtered_df['tipo'].value_counts()
            if not type_counts.empty:
                fig_pie = px.pie(
                    values=type_counts.values,
                    names=type_counts.index,
                    title="Distribución por tipo de ingrediente"
                )
                fig_pie.update_layout(height=400)
                charts['type_distribution'] = json.loads(json.dumps(fig_pie, cls=plotly.utils.PlotlyJSONEncoder))
        
        # Gráfico 3: Estado de regulación
        if not filtered_df.empty:
            regulation_counts = filtered_df['categoria_regulacion'].value_counts()
            if not regulation_counts.empty:
                fig_regulation = px.bar(
                    x=regulation_counts.index,
                    y=regulation_counts.values,
                    title="Estado de regulación por categoría",
                    color=regulation_counts.values,
                    color_continuous_scale="Blues"
                )
                fig_regulation.update_layout(height=400)
                charts['regulation_status'] = json.loads(json.dumps(fig_regulation, cls=plotly.utils.PlotlyJSONEncoder))
        
        # Gráfico 4: Top ingredientes
        if not filtered_df.empty:
            top_ingredients = filtered_df['ingrediente'].value_counts().head(10)
            if not top_ingredients.empty:
                fig_top = px.bar(
                    x=top_ingredients.values,
                    y=top_ingredients.index,
                    orientation='h',
                    title="Top 10 ingredientes más regulados",
                    labels={'x': 'Número de países', 'y': 'Ingrediente'}
                )
                fig_top.update_layout(height=400, yaxis={'categoryorder': 'total ascending'})
                charts['top_ingredients'] = json.loads(json.dumps(fig_top, cls=plotly.utils.PlotlyJSONEncoder))
        
    except Exception as e:
        logger.error(f"Error generando gráficos de suplementos: {e}")
        raise HTTPException(status_code=500, detail=f"Error generando gráficos: {str(e)}")
    
    return charts

@app.get("/api/suplementos/comparison")
async def get_regulatory_comparison(
    countries: Optional[List[str]] = Query(None, description="Países a comparar"),
    category: Optional[str] = Query(None, description="Categoría regulatoria a comparar"),
    sections: Optional[List[str]] = Query(None, description="Secciones específicas a comparar")
):
    """Obtener comparación regulatoria entre países"""
    
    try:
        data = regulatory_data.get("regulatory_data", {})
        
        # Filtrar por países si se especifican
        if countries:
            filtered_data = {k: v for k, v in data.items() if k in countries}
        else:
            filtered_data = data
        
        # Si se especifican secciones, filtrar solo esas
        if sections:
            result = {}
            for country, country_data in filtered_data.items():
                result[country] = {
                    "country_code": country_data.get("country_code", ""),
                    "sections": {
                        section: country_data.get("sections", {}).get(section, {})
                        for section in sections
                        if section in country_data.get("sections", {})
                    }
                }
        else:
            result = filtered_data
        
        return {
            "data": result,
            "metadata": {
                "total_countries": len(result),
                "available_sections": list(set(
                    section for country_data in result.values()
                    for section in country_data.get("sections", {}).keys()
                )),
                "comparison_date": regulatory_data.get("metadata", {}).get("last_updated", "2023-12-01")
            }
        }
        
    except Exception as e:
        logger.error(f"Error en comparación regulatoria: {e}")
        raise HTTPException(status_code=500, detail=f"Error obteniendo comparación: {str(e)}")

# Nueva función para obtener secciones disponibles
@app.get("/api/suplementos/regulatory-sections")
async def get_regulatory_sections():
    """Obtener lista de secciones regulatorias disponibles"""
    try:
        data = regulatory_data.get("regulatory_data", {})
        
        # Recopilar todas las secciones únicas
        all_sections = set()
        for country_data in data.values():
            sections = country_data.get("sections", {})
            all_sections.update(sections.keys())
        
        # Organizar por categorías
        sections_by_type = {}
        for country_data in data.values():
            for section_key, section_data in country_data.get("sections", {}).items():
                section_type = section_data.get("type", "general")
                if section_type not in sections_by_type:
                    sections_by_type[section_type] = []
                
                section_info = {
                    "key": section_key,
                    "title": section_data.get("title", section_key),
                    "type": section_type
                }
                
                if section_info not in sections_by_type[section_type]:
                    sections_by_type[section_type].append(section_info)
        
        return {
            "sections": list(all_sections),
            "sections_by_type": sections_by_type,
            "total_sections": len(all_sections)
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo secciones: {e}")
        raise HTTPException(status_code=500, detail=f"Error obteniendo secciones: {str(e)}")

# Nueva función para obtener estadísticas regulatorias
@app.get("/api/suplementos/regulatory-stats")
async def get_regulatory_stats():
    """Obtener estadísticas del marco regulatorio"""
    try:
        data = regulatory_data.get("regulatory_data", {})
        
        stats = {
            "total_countries": len(data),
            "by_category": {},
            "by_registration_type": {},
            "health_claims_permitted": 0,
            "average_approval_times": {},
            "countries_list": list(data.keys())
        }
        
        for country, country_data in data.items():
            sections = country_data.get("sections", {})
            
            # Categoría regulatoria
            category = sections.get("categoria_regulatoria", {}).get("value", "No especificada")
            stats["by_category"][category] = stats["by_category"].get(category, 0) + 1
            
            # Tipo de registro
            reg_type = sections.get("proceso_registro", {}).get("value", "No especificado")
            stats["by_registration_type"][reg_type] = stats["by_registration_type"].get(reg_type, 0) + 1
            
            # Declaraciones de salud
            health_claims = sections.get("propiedades_salud", {})
            if health_claims.get("permitted", False):
                stats["health_claims_permitted"] += 1
        
        return stats
        
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {e}")
        raise HTTPException(status_code=500, detail=f"Error obteniendo estadísticas: {str(e)}")

# ==============================================
# ENDPOINTS DE SALUD Y UTILIDADES
# ==============================================

@app.get("/health")
async def health_check():
    """Health check para Render"""
    return {
        "status": "healthy",
        "data_loaded": {
            "moleculas": len(data_cache.get('moleculas', [])),
            "suplementos_principal": len(data_cache.get('suplementos_principal', [])),
            "suplementos_referencias": len(data_cache.get('suplementos_referencias', []))
        }
    }

@app.get("/api/reload-data")
async def reload_data():
    """Recargar datos manualmente (útil para desarrollo)"""
    try:
        await load_data_on_startup()
        return {"message": "Datos recargados exitosamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error recargando datos: {str(e)}")

# ==============================================
# MANEJADORES DE ERRORES
# ==============================================

@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return JSONResponse(
        status_code=404,
        content={"message": "Endpoint no encontrado"}
    )

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    logger.error(f"Error interno: {exc}")
    return JSONResponse(
        status_code=500,
        content={"message": "Error interno del servidor"}
    )

# ==============================================
# PUNTO DE ENTRADA
# ==============================================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        log_level="info",
        access_log=True
    )