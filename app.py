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
    """Función para hacer proxy a Streamlit"""
    resp = None  # Inicializar la variable
    
    try:
        # Construir URL completa
        if subpath:
            url = f"{target_url}/{subpath}"
        else:
            url = target_url
        
        # Agregar query parameters
        if request.query_string:
            url += f"?{request.query_string.decode()}"
        
        # Headers para el proxy
        headers = {}
        for key, value in request.headers:
            if key.lower() not in ['host', 'content-length']:
                headers[key] = value
        
        # Hacer request a Streamlit según el método
        if request.method == 'HEAD':
            resp = requests.head(url, headers=headers, timeout=30)
            return Response('', status=resp.status_code, headers=dict(resp.headers))
        elif request.method == 'GET':
            resp = requests.get(url, headers=headers, stream=True, timeout=30)
        elif request.method == 'POST':
            resp = requests.post(url, 
                               data=request.get_data(),
                               headers=headers,
                               stream=True,
                               timeout=30)
        else:
            resp = requests.request(request.method, url, 
                                  data=request.get_data(),
                                  headers=headers,
                                  stream=True,
                                  timeout=30)
        
        # Modificar headers de respuesta
        response_headers = dict(resp.headers)
        response_headers.pop('content-encoding', None)
        response_headers.pop('content-length', None)
        
        # Crear respuesta streaming
        def generate():
            for chunk in resp.iter_content(chunk_size=8192):
                if chunk:
                    yield chunk
        
        return Response(
            generate(),
            status=resp.status_code,
            headers=response_headers
        )
        
    except requests.exceptions.ConnectionError:
        logger.error(f"No se pudo conectar a {target_url}")
        return render_error_page("Dashboard no disponible", 
                                "El dashboard aún se está iniciando. Intenta en unos segundos.")
    except requests.exceptions.Timeout:
        logger.error(f"Timeout conectando a {target_url}")
        return render_error_page("Timeout", 
                                "El dashboard tardó demasiado en responder.")
    except Exception as e:
        logger.error(f"Error en proxy: {e}")
        return render_error_page("Error interno", 
                                f"Error: {str(e)}")

# Bloquear acceso directo a puertos de Streamlit
@app.route('/block-direct-access')
def block_direct():
    return "Acceso directo no permitido", 403

def start_streamlit_dashboards():
    """Iniciar dashboards con configuración CORS corregida"""
    logger.info("Iniciando dashboards de Streamlit...")
    
    try:
        # Dashboard moléculas con CORS habilitado
        subprocess.Popen([
            'python', '-m', 'streamlit', 'run', 'dashboard_moleculas.py',
            '--server.port', '8502',
            '--server.address', '127.0.0.1',
            '--server.headless', 'true',
            '--browser.gatherUsageStats', 'false',
            '--server.enableXsrfProtection', 'false'  # Deshabilitar XSRF
        ])
        
        # Dashboard suplementos con CORS habilitado
        subprocess.Popen([
            'python', '-m', 'streamlit', 'run', 'dashboard_suplementos_test.py',
            '--server.port', '8503',
            '--server.address', '127.0.0.1',
            '--server.headless', 'true',
            '--browser.gatherUsageStats', 'false',
            '--server.enableXsrfProtection', 'false'  # Deshabilitar XSRF
        ])
        
        logger.info("Dashboards iniciados")
        
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