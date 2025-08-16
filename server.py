#!/usr/bin/env python3
"""
Servidor corregido para Portal ILAR
Redirige automáticamente a login.html y evita el directory listing
"""

import os
import sys
import subprocess
import threading
import time
import webbrowser
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
import socketserver
from urllib.parse import urlparse

class ILARRequestHandler(SimpleHTTPRequestHandler):
    """Custom request handler que redirige root a login.html y evita directory listing"""
    
    def end_headers(self):
        # Agregar headers CORS y de seguridad
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        # Evitar que se muestren archivos de código
        self.send_header('X-Content-Type-Options', 'nosniff')
        super().end_headers()
    
    def do_GET(self):
        # Parsear la URL
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        # Redirecciones principales
        if path == '/' or path == '':
            # Redirigir root a login.html
            self.send_response(302)
            self.send_header('Location', '/login.html')
            self.end_headers()
            return
        
        # Evitar acceso a archivos sensibles
        forbidden_extensions = ['.py', '.toml', '.txt', '.csv', '.xlsx']
        forbidden_files = ['server.py', 'requirements.txt', '.gitignore']
        forbidden_dirs = ['.streamlit', 'venv', '__pycache__']
        
        # Verificar si es un archivo prohibido
        file_path = path.lstrip('/')
        
        # Prohibir archivos específicos
        if any(file_path.endswith(ext) for ext in forbidden_extensions):
            if not file_path.startswith('static/'):  # Permitir archivos JS/CSS en static
                self.send_error(403, "Acceso denegado")
                return
        
        if any(forbidden in file_path for forbidden in forbidden_files + forbidden_dirs):
            self.send_error(403, "Acceso denegado")
            return
        
        # Evitar directory listing
        if path.endswith('/') and path != '/':
            self.send_error(403, "Acceso denegado")
            return
        
        # Servir archivos permitidos
        allowed_files = [
            'login.html', 
            'dashboard.html',
            'static/styles.css',
            'static/auth.js',
            'static/dashboard.js',
            'static/config.js'
        ]
        
        if file_path in allowed_files or file_path.startswith('static/'):
            # Verificar que el archivo existe
            if os.path.exists(file_path):
                return super().do_GET()
            else:
                self.send_error(404, "Archivo no encontrado")
                return
        
        # Para cualquier otro archivo, denegar acceso
        self.send_error(403, "Acceso denegado")
    
    def list_directory(self, path):
        """Sobrescribir para evitar directory listing"""
        self.send_error(403, "Directory listing deshabilitado")
        return None

def check_port_available(port):
    """Verifica si un puerto está disponible"""
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('localhost', port))
            return True
        except OSError:
            return False

def check_required_files():
    """Verificar que los archivos necesarios existan"""
    required_files = [
        'login.html',
        'dashboard.html',
        'static/styles.css',
        'static/auth.js',
        'static/dashboard.js',
        'static/config.js'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print("❌ Archivos faltantes:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    
    print("✅ Todos los archivos requeridos están presentes")
    return True

def start_streamlit_dashboard(dashboard_name, port):
    """Inicia un dashboard de Streamlit en un puerto específico"""
    
    # Verificar si el archivo del dashboard existe
    dashboard_file = f'dashboard_{dashboard_name}.py'
    if not os.path.exists(dashboard_file):
        print(f"⚠️  Archivo {dashboard_file} no encontrado")
        return None
    
    # Comando para ejecutar Streamlit
    cmd = [
        sys.executable, '-m', 'streamlit', 'run', 
        dashboard_file,
        '--server.port', str(port),
        '--server.headless', 'true',
        '--browser.gatherUsageStats', 'false',
        '--server.enableCORS', 'false',
        '--server.enableXsrfProtection', 'false'
    ]
    
    try:
        # Iniciar proceso de Streamlit
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        print(f"🚀 Dashboard {dashboard_name} iniciado en puerto {port}")
        return process
        
    except Exception as e:
        print(f"❌ Error iniciando dashboard {dashboard_name}: {e}")
        return None

def start_web_server(port=8080):
    """Inicia el servidor web para las páginas HTML"""
    try:
        # Cambiar al directorio actual
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        
        # Configurar servidor
        with socketserver.TCPServer(("", port), ILARRequestHandler) as httpd:
            print(f"🌐 Servidor web iniciado en http://localhost:{port}")
            print(f"📝 Acceso directo: http://localhost:{port}/login.html")
            httpd.serve_forever()
            
    except Exception as e:
        print(f"❌ Error iniciando servidor web: {e}")

def main():
    """Función principal"""
    print("🧬 PORTAL ILAR - Iniciando servicios...")
    print("=" * 50)
    
    # Verificar archivos requeridos
    if not check_required_files():
        print("\n❌ Por favor verifica que todos los archivos estén presentes")
        return
    
    # Puertos para cada servicio
    WEB_PORT = 8080
    MOLECULAS_PORT = 8502
    SUPLEMENTOS_PORT = 8503
    
    # Verificar que los puertos estén disponibles
    ports_to_check = [WEB_PORT, MOLECULAS_PORT, SUPLEMENTOS_PORT]
    for port in ports_to_check:
        if not check_port_available(port):
            print(f"❌ Puerto {port} no disponible")
            return
    
    # Lista para mantener referencia a los procesos
    processes = []
    
    try:
        # 1. Iniciar dashboards de Streamlit
        print("\n📊 Iniciando dashboards de Streamlit...")
        
        # Dashboard de moléculas
        moleculas_process = start_streamlit_dashboard('moleculas', MOLECULAS_PORT)
        if moleculas_process:
            processes.append(moleculas_process)
        
        # Dashboard de suplementos
        suplementos_process = start_streamlit_dashboard('suplementos', SUPLEMENTOS_PORT)
        if suplementos_process:
            processes.append(suplementos_process)
        
        # Esperar un poco para que Streamlit se inicie
        print("⏳ Esperando que los dashboards se inicien...")
        time.sleep(3)
        
        # 2. Iniciar servidor web en un hilo separado
        print("\n🌐 Iniciando servidor web...")
        web_thread = threading.Thread(
            target=start_web_server, 
            args=(WEB_PORT,),
            daemon=True
        )
        web_thread.start()
        
        # Esperar un poco más
        time.sleep(2)
        
        # 3. Mostrar información de acceso
        print(f"\n🎉 Portal ILAR iniciado exitosamente!")
        print(f"🔗 Accede en: http://localhost:{WEB_PORT}")
        print(f"📝 Login directo: http://localhost:{WEB_PORT}/login.html")
        print(f"📊 Dashboard Moléculas: http://localhost:{MOLECULAS_PORT}")
        print(f"📊 Dashboard Suplementos: http://localhost:{SUPLEMENTOS_PORT}")
        print("\n💡 Presiona Ctrl+C para detener todos los servicios")
        print("⚠️  NOTA: Ahora solo se pueden acceder a archivos permitidos")
        
        # Abrir navegador automáticamente
        try:
            webbrowser.open(f"http://localhost:{WEB_PORT}/login.html")
        except:
            pass
        
        # Mantener el script corriendo
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n🛑 Deteniendo servicios...")
            
    except KeyboardInterrupt:
        print("\n\n🛑 Deteniendo servicios...")
    
    finally:
        # Terminar todos los procesos de Streamlit
        for process in processes:
            try:
                process.terminate()
                process.wait(timeout=5)
            except:
                try:
                    process.kill()
                except:
                    pass
        
        print("✅ Todos los servicios han sido detenidos")

if __name__ == "__main__":
    main()