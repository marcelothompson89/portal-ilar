#!/usr/bin/env python3
"""
Portal ILAR - FastAPI + Plotly
Solución optimizada para producción en Render
"""

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import List, Optional
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


# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cache global para datos
data_cache = {}

async def load_data_on_startup():
    """Cargar todos los datos al iniciar la aplicación"""
    logger.info("🔄 Cargando datos en memoria...")
    
    try:
        # Verificar si el archivo existe
        excel_file = 'Version final Extracto base de datos Mar 2023.xlsx'
        if not os.path.exists(excel_file):
            logger.warning(f"❌ Archivo {excel_file} no encontrado")
            data_cache['moleculas'] = pd.DataFrame()
            return
            
        logger.info(f"📂 Cargando archivo: {excel_file}")
        
        # Cargar datos de moléculas
        df_moleculas = pd.read_excel(
            excel_file, 
            sheet_name='Base en inglés'
        )
        
        # Limpiar duplicados
        key_columns = ['Molecule', 'Country', 'Switch Year', 'Strength']
        df_moleculas = df_moleculas.drop_duplicates()
        df_moleculas = df_moleculas.drop_duplicates(subset=key_columns, keep='first')
        
        # 🔧 Normalizar columnas de texto que usamos
        for col in ['Molecule', 'Country', 'RX-OTC - Molecule', 'RX-OTC - Product', 'Strength']:
            if col in df_moleculas.columns:
                df_moleculas[col] = df_moleculas[col].astype(str).str.strip()

        # 🔧 Coerción segura del año: convierte '-', '—', '', etc. en NaN y luego a numérico
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
    
    try:
        # Cargar datos de suplementos (ejemplo - ajusta según tu archivo)
        # df_suplementos = pd.read_excel('suplementos_data.xlsx')
        
        # Datos de ejemplo por ahora
        df_suplementos = pd.DataFrame({
            'Country': ['Argentina', 'Brazil', 'Chile', 'Colombia', 'Mexico', 'Peru'] * 20,
            'Ingredient': ['Vitamin C', 'Vitamin D', 'Omega 3', 'Probiotics', 'Iron', 'Calcium'] * 20,
            'Regulation_Status': ['Approved', 'Restricted', 'Pending', 'Banned', 'Approved', 'Under Review'] * 20,
            'Category': ['Vitamins', 'Vitamins', 'Fatty Acids', 'Probiotics', 'Minerals', 'Minerals'] * 20,
            'Max_Dose': [1000, 800, 500, 1000000, 18, 1200] * 20,
            'Regulatory_Framework': ['ANMAT', 'ANVISA', 'ISP', 'INVIMA', 'COFEPRIS', 'DIGEMID'] * 20
        })
        
        data_cache['suplementos'] = df_suplementos
        logger.info(f"✅ Suplementos cargados: {len(df_suplementos)} registros")
        
    except Exception as e:
        logger.error(f"❌ Error cargando suplementos: {e}")
        data_cache['suplementos'] = pd.DataFrame()

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

# RUTAS PRINCIPALES
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Página de inicio - servir página de carga o redirigir a login"""
    # Si existe el archivo de carga temporal, servirlo
    if os.path.exists('loading_temp.html'):
        with open('loading_temp.html', 'r', encoding='utf-8') as f:
            content = f.read()
        return HTMLResponse(content=content)
    else:
        # Si no, redirigir a login
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

# DASHBOARDS INTEGRADOS
@app.get("/analytics/molecular-data", response_class=HTMLResponse)
async def dashboard_moleculas(request: Request):
    """Dashboard de moléculas"""
    return templates.TemplateResponse("dashboard_moleculas.html", {"request": request})

@app.get("/analytics/supplement-regulations", response_class=HTMLResponse)
async def dashboard_suplementos(request: Request):
    """Dashboard de suplementos"""
    return templates.TemplateResponse("dashboard_suplementos.html", {"request": request})

# APIs DE DATOS
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

    # Coerción segura para calcular rango de años
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
    """Obtener datos de moléculas con paginación (JSON-safe: sin NaN/Inf/NaT)"""
    df = data_cache.get('moleculas')
    if df is None or df.empty:
        raise HTTPException(status_code=500, detail="Datos de moléculas no disponibles")

    # Filtros
    filtered_df = df.copy()
    if molecule and molecule != "all":
        filtered_df = filtered_df[filtered_df['Molecule'] == molecule]
    if countries and len(countries) > 0:
        filtered_df = filtered_df[filtered_df['Country'].isin(countries)]

    # Total de registros filtrados
    total_records = len(filtered_df)
    
    # Paginación
    paginated_df = filtered_df.iloc[offset:offset + limit].copy()

    # --- Fechas → string ISO ---
    for c in paginated_df.columns:
        col = paginated_df[c]
        if is_datetime64_any_dtype(col) or is_datetime64tz_dtype(col):
            paginated_df[c] = pd.to_datetime(col, errors="coerce").dt.strftime("%Y-%m-%d")

    # --- JSON safe: reemplazar NaN/NaT/±Inf por None ---
    paginated_df = paginated_df.replace([pd.NA, pd.NaT, np.nan, np.inf, -np.inf], None)
    paginated_df = paginated_df.where(pd.notna(paginated_df), None)

    payload = {
        "data": paginated_df.to_dict("records"),
        "pagination": {
            "total": total_records,
            "limit": limit,
            "offset": offset,
            "has_next": offset + limit < total_records
        }
    }

    # Encoder de FastAPI que convierte tipos numpy/pandas a JSON válido
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
        # Gráfico 1: Moléculas únicas por país (top 15)
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
                fig_pie.update_layout(
                    height=400,
                    margin=dict(l=40, r=40, t=60, b=40)
                )
                charts['rx_otc_distribution'] = json.loads(json.dumps(fig_pie, cls=plotly.utils.PlotlyJSONEncoder))
        
        # Gráfico 3: Timeline de switches (si hay datos de años válidos)
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
                    fig_timeline.update_layout(
                        height=400,
                        xaxis_title="Año",
                        yaxis_title="Número de switches"
                    )
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

@app.get("/api/suplementos/stats")
async def get_suplementos_stats():
    """Estadísticas básicas de suplementos"""
    
    df = data_cache.get('suplementos')
    if df is None or df.empty:
        raise HTTPException(status_code=500, detail="Datos de suplementos no disponibles")
    
    return {
        "total_records": len(df),
        "unique_countries": df['Country'].nunique(),
        "unique_ingredients": df['Ingredient'].nunique(),
        "unique_categories": df['Category'].nunique(),
        "available_countries": sorted(df['Country'].unique().tolist()),
        "available_categories": sorted(df['Category'].unique().tolist()),
        "regulation_statuses": df['Regulation_Status'].value_counts().to_dict()
    }

@app.get("/api/suplementos/charts")
async def get_suplementos_charts(
    countries: Optional[List[str]] = Query(None),
    category: Optional[str] = Query(None)
):
    """Gráficos para dashboard de suplementos"""
    
    df = data_cache.get('suplementos')
    if df is None or df.empty:
        raise HTTPException(status_code=500, detail="Datos de suplementos no disponibles")
    
    # Aplicar filtros
    filtered_df = df.copy()
    if countries:
        filtered_df = filtered_df[filtered_df['Country'].isin(countries)]
    if category and category != "all":
        filtered_df = filtered_df[filtered_df['Category'] == category]
    
    charts = {}
    
    try:
        # Gráfico 1: Status regulatorio por país
        status_by_country = filtered_df.groupby(['Country', 'Regulation_Status']).size().unstack(fill_value=0)
        fig_status = px.bar(
            status_by_country,
            title="Estado regulatorio por país",
            labels={'value': 'Número de ingredientes', 'index': 'País'}
        )
        fig_status.update_layout(height=400, xaxis_tickangle=-45)
        charts['status_by_country'] = json.loads(json.dumps(fig_status, cls=plotly.utils.PlotlyJSONEncoder))
        
        # Gráfico 2: Distribución por categoría
        category_counts = filtered_df['Category'].value_counts()
        fig_categories = px.pie(
            values=category_counts.values,
            names=category_counts.index,
            title="Distribución por categoría de ingredientes"
        )
        fig_categories.update_layout(height=400)
        charts['category_distribution'] = json.loads(json.dumps(fig_categories, cls=plotly.utils.PlotlyJSONEncoder))
        
        # Gráfico 3: Heatmap regulatorio
        regulation_matrix = filtered_df.pivot_table(
            index='Country', 
            columns='Regulation_Status', 
            values='Ingredient', 
            aggfunc='count', 
            fill_value=0
        )
        fig_heatmap = px.imshow(
            regulation_matrix.values,
            x=regulation_matrix.columns,
            y=regulation_matrix.index,
            title="Matriz regulatoria por país",
            color_continuous_scale="RdYlBu_r"
        )
        fig_heatmap.update_layout(height=400)
        charts['regulation_heatmap'] = json.loads(json.dumps(fig_heatmap, cls=plotly.utils.PlotlyJSONEncoder))
        
    except Exception as e:
        logger.error(f"Error generando gráficos de suplementos: {e}")
        raise HTTPException(status_code=500, detail=f"Error generando gráficos: {str(e)}")
    
    return charts

# ENDPOINTS DE SALUD
@app.get("/health")
async def health_check():
    """Health check para Render"""
    return {
        "status": "healthy",
        "data_loaded": {
            "moleculas": len(data_cache.get('moleculas', [])),
            "suplementos": len(data_cache.get('suplementos', []))
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

# Manejador de errores
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

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        log_level="info",
        access_log=True
    )