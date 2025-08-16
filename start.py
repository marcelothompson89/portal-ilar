#!/usr/bin/env python3
"""
Script de inicio para desarrollo local del Portal ILAR con FastAPI
"""

import os
import sys
import uvicorn
import webbrowser
import time
from pathlib import Path

def check_files():
    """Verificar que los archivos necesarios existan"""
    required_files = [
        'main.py',
        'requirements.txt',
        'templates/dashboard_moleculas.html',
        'templates/login.html',
        'templates/dashboard.html'
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
    
    print("✅ Todos los archivos necesarios están presentes")
    return True

def create_directories():
    """Crear directorios necesarios"""
    directories = ['templates', 'static']
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"📁 Directorio {directory} verificado")

def main():
    """Función principal"""
    print("🧬 Portal ILAR - FastAPI")
    print("=" * 40)
    
    # Crear directorios necesarios
    create_directories()
    
    # Verificar archivos
    if not check_files():
        print("\n❌ Por favor crea los archivos faltantes antes de continuar")
        return
    
    # Configuración del servidor
    host = "127.0.0.1"
    port = 8000
    
    print(f"\n🚀 Iniciando servidor FastAPI en http://{host}:{port}")
    print(f"📝 Login: http://{host}:{port}/login.html")
    print(f"📊 Dashboard Moléculas: http://{host}:{port}/analytics/molecular-data")
    print(f"📊 Dashboard Suplementos: http://{host}:{port}/analytics/supplement-regulations")
    print(f"🔍 API Docs: http://{host}:{port}/docs")
    print("\n💡 Presiona Ctrl+C para detener el servidor")
    
    # Abrir navegador después de un pequeño delay
    def open_browser():
        time.sleep(2)
        try:
            webbrowser.open(f"http://{host}:{port}/login.html")
        except:
            pass
    
    import threading
    browser_thread = threading.Thread(target=open_browser, daemon=True)
    browser_thread.start()
    
    # Iniciar servidor
    try:
        uvicorn.run(
            "main:app",
            host=host,
            port=port,
            reload=True,  # Auto-reload en desarrollo
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n\n🛑 Servidor detenido")
    except Exception as e:
        print(f"\n❌ Error iniciando servidor: {e}")

if __name__ == "__main__":
    main()