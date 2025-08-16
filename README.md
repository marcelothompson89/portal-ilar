# Portal ILAR - Instrucciones de Setup Local

## 📋 Requisitos Previos

1. Python 3.8 o superior
2. Cuenta en [Supabase](https://supabase.com) (gratuita)

## 🚀 Setup Paso a Paso

### 1. Configurar Supabase

1. Ve a [supabase.com](https://supabase.com) y crea una cuenta
2. Crea un nuevo proyecto
3. En el panel de tu proyecto, ve a **Settings > API**
4. Copia tu **Project URL** y **anon public key**

### 2. Configurar el Proyecto Local

1. **Clona o descarga el proyecto**
```bash
git clone tu-repositorio
cd portal-ilar
```

2. **Instala las dependencias**
```bash
pip install -r requirements.txt
```

3. **Configura las credenciales**

Crea el archivo `.streamlit/secrets.toml`:
```bash
mkdir .streamlit
touch .streamlit/secrets.toml
```

Edita `.streamlit/secrets.toml` con tus credenciales:
```toml
SUPABASE_URL = "https://tu-proyecto-id.supabase.co"
SUPABASE_ANON_KEY = "tu_clave_anonima_muy_larga_aqui"
```

4. **Configura las credenciales en JavaScript**

Edita `static/auth.js` y `static/dashboard.js`, cambia las líneas:
```javascript
const SUPABASE_URL = 'https://tu-proyecto-id.supabase.co';
const SUPABASE_ANON_KEY = 'tu_clave_anonima_aqui';
```

### 3. Estructura del Proyecto

Organiza tu proyecto con esta estructura:
```
portal-ilar/
├── login.html                     # ✨ Página de login (HTML)
├── dashboard.html                  # ✨ Landing de dashboards (HTML)
├── static/
│   ├── styles.css                 # ✨ Estilos CSS
│   ├── auth.js                    # ✨ Lógica de autenticación
│   └── dashboard.js               # ✨ Lógica del dashboard
├── server.py                      # 🚀 Servidor principal
├── streamlit_app.py               # 📊 App de Streamlit
├── requirements.txt               # 📦 Dependencias
├── dashboard_moleculas.py         # 📊 Tu dashboard de moléculas
└── dashboard_suplementos.py       # 📊 Tu dashboard de suplementos
```

### 4. Configurar Supabase Authentication

En tu proyecto de Supabase:

1. Ve a **Authentication > Settings**
2. En **Site URL**, agrega: `http://localhost:8080`
3. En **Redirect URLs**, agrega: `http://localhost:8080`

### 5. Integrar tus Dashboards

1. **Copia tus dashboards existentes:**
```bash
cp tu_dashboard_moleculas.py dashboard_moleculas.py
cp tu_dashboard_suplementos.py dashboard_suplementos.py
```

2. **Asegúrate de que tengan todas las dependencias necesarias**

### 6. Ejecutar el Portal

**Opción 1: Ejecutar todo automáticamente (Recomendado)**
```bash
python server.py
```

**Opción 2: Ejecutar manualmente**
```bash
# Terminal 1: Servidor web
python -m http.server 8080

# Terminal 2: Dashboard moléculas
streamlit run dashboard_moleculas.py --server.port 8502

# Terminal 3: Dashboard suplementos  
streamlit run dashboard_suplementos.py --server.port 8503
```

## 🎯 **Flujo Completo:**

1. **Usuario accede a** `http://localhost:8080`
2. **Ve página de login HTML** (moderna y atractiva)
3. **Inicia sesión** → Redirige a `dashboard.html`
4. **Ve landing con botones** para cada dashboard
5. **Hace clic en botón** → Abre dashboard de Streamlit en nueva pestaña
6. **Accede al contenido** protegido

## 🔐 Gestión de Usuarios

### Para el Cliente (Administrador)

1. **Crear usuarios desde el Dashboard de Supabase:**
   - Ve a **Authentication > Users** en tu proyecto Supabase
   - Haz clic en **Add user**
   - Ingresa email y contraseña temporal
   - El usuario recibirá un email para confirmar

2. **Gestionar usuarios existentes:**
   - Ver lista de usuarios registrados
   - Desactivar/activar usuarios
   - Resetear contraseñas
   - Ver logs de acceso

### Para Usuarios Finales

1. **Registro:** Los usuarios pueden registrarse desde la interfaz HTML
2. **Login:** Acceso con email y contraseña en la página moderna
3. **Recuperación:** Función "Olvidé mi contraseña" disponible

## 🎨 **Características de la Nueva Interfaz:**

### ✨ **Página de Login (`login.html`):**
- Diseño moderno con paleta ILAR
- Pestañas para Login/Registro
- Validación en tiempo real
- Medidor de fortaleza de contraseña
- Recuperación de contraseña
- Animaciones suaves
- Responsive design

### 🚀 **Landing Dashboard (`dashboard.html`):**
- Tarjetas interactivas para cada dashboard
- Estadísticas animadas
- Información del usuario
- Actualizaciones recientes
- Botones que abren dashboards en nuevas pestañas
- Diseño completamente responsive

## 🔧 Personalización

### Cambiar URLs de Dashboards

En `static/dashboard.js`, modifica:
```javascript
const DASHBOARD_URLS = {
    moleculas: 'http://localhost:8502',
    suplementos: 'http://localhost:8503'
};
```

### Agregar Más Dashboards

1. **Agrega la tarjeta en `dashboard.html`**
2. **Actualiza `DASHBOARD_URLS` en `dashboard.js`**
3. **Agrega la función en `openDashboard()`**

## 🚀 Deployment en Render

Una vez que funcione localmente:

1. **Sube el código a GitHub**
2. **Conecta Render con tu repositorio**
3. **Configura las variables de entorno en Render:**
   - `SUPABASE_URL`
   - `SUPABASE_ANON_KEY`
4. **Actualiza las URLs en Supabase** para el dominio de producción
5. **Actualiza las URLs en los archivos JS** para producción

## 🔧 Solución de Problemas

### Error de Conexión a Supabase
- Verifica que las credenciales sean correctas en ambos lugares (secrets.toml y archivos JS)
- Asegúrate de que el proyecto Supabase esté activo
- Revisa que las URLs de redirect estén configuradas

### Dashboards No Cargan
- Verifica que los archivos `dashboard_moleculas.py` y `dashboard_suplementos.py` existan
- Asegúrate de que no haya conflictos de puertos
- Revisa las dependencias específicas de cada dashboard

### Problemas de Autenticación
- Limpia las cookies del navegador
- Verifica que el email esté confirmado en Supabase
- Revisa los logs en el panel de Supabase

## 🎯 **Ventajas de esta Arquitectura:**

- ✅ **Login moderno** con HTML/CSS/JS nativo
- ✅ **Landing atractivo** para seleccionar dashboards
- ✅ **Dashboards completos** en Streamlit (sin limitaciones)
- ✅ **Autenticación robusta** con Supabase
- ✅ **Fácil mantenimiento** - cada parte independiente
- ✅ **Escalable** - agregar dashboards es sencillo
- ✅ **Responsive** - funciona en móviles y desktop

## 📱 **Funcionalidades Avanzadas:**

### 🎨 **Interfaz:**
- Animaciones CSS3 suaves
- Paleta de colores ILAR
- Modo responsive completo
- Notificaciones en tiempo real
- Loading states animados

### 🔐 **Autenticación:**
- Login/registro seguro
- Recuperación de contraseña
- Sesiones persistentes
- Logout automático por inactividad
- Validación en tiempo real

### ⚡ **Performance:**
- Carga rápida de páginas HTML
- Dashboards de Streamlit en paralelo
- Notificaciones de estado de conexión
- Manejo de errores gracioso

## 🛠️ **Comandos Útiles:**

```bash
# Setup completo automático
python setup.py

# Ejecutar todo el portal
python server.py

# Solo servidor web
python -m http.server 8080

# Solo dashboard moléculas
streamlit run dashboard_moleculas.py --server.port 8502

# Solo dashboard suplementos
streamlit run dashboard_suplementos.py --server.port 8503

# Instalar dependencias
pip install -r requirements.txt
```

## 📞 Soporte

Si tienes problemas:
1. Revisa los logs en la terminal donde ejecutas `python server.py`
2. Verifica los logs en el panel de Supabase
3. Asegúrate de que todas las dependencias estén instaladas
4. Comprueba que los puertos 8080, 8502, 8503 estén libres

## 🔒 Seguridad

- **NUNCA** subas archivos con credenciales reales a Git
- Agrega `static/auth.js` y `static/dashboard.js` a `.gitignore` si contienen credenciales
- Usa variables de entorno en producción
- Revisa periódicamente los usuarios activos en Supabase
- Configura rate limiting en Supabase si es necesario

## 🎯 **Próximos Pasos Sugeridos:**

1. **Probar localmente** con `python server.py`
2. **Configurar dominio** personalizado
3. **Agregar más dashboards** según necesidad
4. **Implementar analytics** de uso
5. **Configurar backups** de Supabase
6. **Agregar notificaciones** push# Portal ILAR - Instrucciones de Setup Local

## 📋 Requisitos Previos

1. Python 3.8 o superior
2. Cuenta en [Supabase](https://supabase.com) (gratuita)

## 🚀 Setup Paso a Paso

### 1. Configurar Supabase

1. Ve a [supabase.com](https://supabase.com) y crea una cuenta
2. Crea un nuevo proyecto
3. En el panel de tu proyecto, ve a **Settings > API**
4. Copia tu **Project URL** y **anon public key**

### 2. Configurar el Proyecto Local

1. **Clona o descarga el proyecto**
```bash
git clone tu-repositorio
cd portal-ilar
```

2. **Instala las dependencias**
```bash
pip install -r requirements.txt
```

3. **Configura las credenciales**

Crea el archivo `.streamlit/secrets.toml`:
```bash
mkdir .streamlit
touch .streamlit/secrets.toml
```

Edita `.streamlit/secrets.toml` con tus credenciales:
```toml
SUPABASE_URL = "https://tu-proyecto-id.supabase.co"
SUPABASE_ANON_KEY = "tu_clave_anonima_muy_larga_aqui"
```

### 3. Estructura del Proyecto

Organiza tu proyecto con esta estructura:
```
portal-ilar/
├── app.py                          # Archivo principal
├── requirements.txt                # Dependencias
├── .streamlit/
│   └── secrets.toml               # Credenciales (NO subir a git)
├── pages/
│   ├── auth.py                    # Lógica de autenticación
│   └── dashboard_home.py          # Dashboard principal
├── utils/
│   └── supabase_client.py        # Cliente de Supabase
├── dashboard_moleculas.py         # Tu dashboard existente de moléculas
└── dashboard_suplementos.py       # Tu dashboard existente de suplementos
```

### 4. Configurar Supabase Authentication

En tu proyecto de Supabase:

1. Ve a **Authentication > Settings**
2. En **Site URL**, agrega: `http://localhost:8501`
3. En **Redirect URLs**, agrega: `http://localhost:8501`

### 5. Ejecutar el Portal

```bash
streamlit run app.py
```

El portal estará disponible en `http://localhost:8501`

## 🔐 Gestión de Usuarios

### Para el Cliente (Administrador)

1. **Crear usuarios desde el Dashboard de Supabase:**
   - Ve a **Authentication > Users** en tu proyecto Supabase
   - Haz clic en **Add user**
   - Ingresa email y contraseña temporal
   - El usuario recibirá un email para confirmar

2. **Gestionar usuarios existentes:**
   - Ver lista de usuarios registrados
   - Desactivar/activar usuarios
   - Resetear contraseñas
   - Ver logs de acceso

### Para Usuarios Finales

1. **Registro:** Los usuarios pueden registrarse desde la interfaz
2. **Login:** Acceso con email y contraseña
3. **Recuperación:** Función "Olvidé mi contraseña" disponible

## 📊 Integrar tus Dashboards Existentes

### Opción 1: Módulos Separados (Recomendado)

Coloca tus archivos existentes en el directorio raíz:
- `dashboard_moleculas.py`
- `dashboard_suplementos.py`

### Opción 2: Integración en Pages

Crea archivos en `pages/`:
- `pages/dashboard_moleculas.py`
- `pages/dashboard_suplementos.py`

Y modifica las importaciones en `app.py`.

## 🛠️ Personalización

### Cambiar Colores (Paleta ILAR)

En `app.py`, modifica las variables CSS:
```css
--primary-color: #8BC34A    /* Verde principal ILAR */
--secondary-color: #4A90C2  /* Azul secundario */
--accent-color: #689F38     /* Verde oscuro */
```

### Agregar Más Dashboards

1. En `app.py`, agrega la opción al menú:
```python
menu_option = option_menu(
    options=["🏠 Inicio", "🧪 Dashboard Moléculas", "📊 Dashboard Suplementos", "🆕 Nuevo Dashboard"],
    # ...
)
```

2. Agrega la función correspondiente:
```python
elif menu_option == "🆕 Nuevo Dashboard":
    show_nuevo_dashboard()
```

## 🚀 Deployment en Render

Una vez que funcione localmente:

1. **Sube el código a GitHub**
2. **Conecta Render con tu repositorio**
3. **Configura las variables de entorno en Render:**
   - `SUPABASE_URL`
   - `SUPABASE_ANON_KEY`
4. **Actualiza las URLs en Supabase** para el dominio de producción

## 🔧 Solución de Problemas

### Error de Conexión a Supabase
- Verifica que las credenciales sean correctas
- Asegúrate de que el proyecto Supabase esté activo
- Revisa que las URLs de redirect estén configuradas

### Error al Importar Dashboards
- Verifica que los archivos estén en el directorio correcto
- Asegúrate de que no haya conflictos de nombres de variables
- Revisa las dependencias específicas de cada dashboard

### Problemas de Autenticación
- Limpia las cookies del navegador
- Verifica que el email esté confirmado en Supabase
- Revisa los logs en el panel de Supabase

## 📞 Soporte

Si tienes problemas:
1. Revisa los logs en la terminal donde ejecutas Streamlit
2. Verifica los logs en el panel de Supabase
3. Asegúrate de que todas las dependencias estén instaladas

## 🔒 Seguridad

- **NUNCA** subas el archivo `secrets.toml` a Git
- Agrega `.streamlit/secrets.toml` a tu `.gitignore`
- Usa variables de entorno en producción
- Revisa periódicamente los usuarios activos en Supabase