#!/usr/bin/env python3
import os
import subprocess
import threading
import time
import requests
from flask import Flask, send_from_directory, redirect, Response, request
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# URLs internas de Streamlit (no expuestas)
STREAMLIT_MOLECULAS = 'http://localhost:8502'
STREAMLIT_SUPLEMENTOS = 'http://localhost:8503'

@app.route('/')
def home():
    return redirect('/login.html')

@app.route('/<path:filename>')
def serve_static(filename):
    """Servir archivos estáticos"""
    # Solo permitir archivos específicos
    allowed_files = ['login.html', 'dashboard.html']
    if filename in allowed_files:
        return send_from_directory('.', filename)
    return "Archivo no encontrado", 404

@app.route('/static/<path:filename>')
def serve_static_files(filename):
    """Servir archivos de la carpeta static"""
    return send_from_directory('static', filename)

# RUTAS PROXY PARA DASHBOARDS (URLs ocultas)
@app.route('/analytics/molecular-data')
@app.route('/analytics/molecular-data/<path:subpath>')
def proxy_moleculas(subpath=''):
    """Proxy para dashboard de moléculas con URL ofuscada"""
    return proxy_streamlit(STREAMLIT_MOLECULAS, subpath)

@app.route('/analytics/supplement-regulations')
@app.route('/analytics/supplement-regulations/<path:subpath>')
def proxy_suplementos(subpath=''):
    """Proxy para dashboard de suplementos con URL ofuscada"""
    return proxy_streamlit(STREAMLIT_SUPLEMENTOS, subpath)

def proxy_streamlit(target_url, subpath=''):
    """Función helper para hacer proxy a Streamlit"""
    try:
        # Construir URL completa
        if subpath:
            url = f"{target_url}/{subpath}"
        else:
            url = target_url
        
        # Obtener parámetros de query
        if request.query_string:
            url += f"?{request.query_string.decode()}"
        
        # Hacer request al Streamlit interno
        if request.method == 'GET':
            resp = requests.get(url, stream=True)
        elif request.method == 'POST':
            resp = requests.post(url, 
                               data=request.get_data(),
                               headers=dict(request.headers))
        
        # Crear respuesta proxy
        def generate():
            for chunk in resp.iter_content(chunk_size=1024):
                yield chunk
        
        return Response(
            generate(),
            status=resp.status_code,
            headers=dict(resp.headers)
        )
        
    except Exception as e:
        logger.error(f"Error en proxy: {e}")
        return f"Error cargando dashboard: {e}", 500

# Bloquear acceso directo a puertos de Streamlit
@app.route('/block-direct-access')
def block_direct():
    return "Acceso directo no permitido", 403

def start_streamlit_dashboards():
    """Iniciar dashboards de Streamlit SOLO en localhost"""
    logger.info("Iniciando dashboards de Streamlit...")
    
    try:
        # Dashboard de moléculas (solo localhost)
        subprocess.Popen([
            'python', '-m', 'streamlit', 'run', 'dashboard_moleculas.py',
            '--server.port', '8502',
            '--server.address', '127.0.0.1',  # Solo localhost
            '--server.headless', 'true',
            '--browser.gatherUsageStats', 'false',
            '--server.enableCORS', 'false'
        ])
        
        # Dashboard de suplementos (solo localhost)
        subprocess.Popen([
            'python', '-m', 'streamlit', 'run', 'dashboard_suplementos.py',
            '--server.port', '8503',
            '--server.address', '127.0.0.1',  # Solo localhost
            '--server.headless', 'true',
            '--browser.gatherUsageStats', 'false',
            '--server.enableCORS', 'false'
        ])
        
        logger.info("Dashboards iniciados en localhost únicamente")
        
    except Exception as e:
        logger.error(f"Error iniciando dashboards: {e}")

if __name__ == '__main__':
    # Iniciar Streamlit en background
    streamlit_thread = threading.Thread(target=start_streamlit_dashboards)
    streamlit_thread.daemon = True
    streamlit_thread.start()
    
    # Esperar a que Streamlit inicie
    time.sleep(10)
    
    # Iniciar Flask
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"Servidor iniciado en puerto {port}")
    app.run(host='0.0.0.0', port=port, debug=False)