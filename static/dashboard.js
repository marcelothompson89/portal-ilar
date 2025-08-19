// ==============================================
// DASHBOARD PORTAL ILAR
// ==============================================
// La configuración se carga desde config.js - NO declarar variables aquí

// Inicialización
document.addEventListener('DOMContentLoaded', function() {
    // Verificar que la configuración esté cargada
    if (!window.ILAR_CONFIG) {
        console.error('❌ Configuración no encontrada. Verifica que config.js se cargue primero.');
        showNotification('Error de configuración. Recarga la página.', 'error');
        return;
    }
    
    // Verificar que Supabase esté disponible
    if (!window.supabase) {
        console.error('❌ Supabase no encontrado. Verifica la conexión a internet.');
        showNotification('Error cargando Supabase. Verifica tu conexión.', 'error');
        return;
    }
    
    initializeDashboard();
});

function initializeDashboard() {
    try {
        // Crear cliente de Supabase usando la configuración global
        window.supabaseClient = window.supabase.createClient(
            window.ILAR_CONFIG.SUPABASE_URL, 
            window.ILAR_CONFIG.SUPABASE_ANON_KEY
        );
        
        console.log('✅ Cliente de Supabase inicializado en dashboard');
        
        checkAuthentication();
        loadUserInfo();
        initializeAnimations();
        updateLastLogin();
        setupAuthStateListener();
        
    } catch (error) {
        console.error('❌ Error inicializando dashboard:', error);
        showNotification('Error de inicialización. Recarga la página.', 'error');
    }
}

// ==============================================
// AUTENTICACIÓN
// ==============================================
async function checkAuthentication() {
    try {
        const { data: { session } } = await window.supabaseClient.auth.getSession();
        
        if (!session) {
            // No hay sesión activa, redirigir a login
            console.log('No hay sesión activa, redirigiendo a login...');
            window.location.href = 'login.html';
            return;
        }
        
        // Usuario autenticado, continuar cargando la página
        console.log('Usuario autenticado:', session.user.email);
        
    } catch (error) {
        console.error('Error checking authentication:', error);
        window.location.href = 'login.html';
    }
}

async function loadUserInfo() {
    try {
        const { data: { user } } = await window.supabaseClient.auth.getUser();
        
        if (user) {
            updateUserDisplay(user);
        }
        
    } catch (error) {
        console.error('Error loading user info:', error);
    }
}

function updateUserDisplay(user) {
    const userNameElement = document.getElementById('userName');
    const userEmailElement = document.getElementById('userEmail');
    const userAvatarElement = document.getElementById('userAvatar');
    
    // Obtener nombre del usuario
    let displayName = 'Usuario';
    if (user.user_metadata) {
        const { first_name, last_name, full_name } = user.user_metadata;
        if (full_name) {
            displayName = full_name;
        } else if (first_name && last_name) {
            displayName = `${first_name} ${last_name}`;
        } else if (first_name) {
            displayName = first_name;
        }
    }
    
    // Si no hay metadata, usar parte del email
    if (displayName === 'Usuario' && user.email) {
        displayName = user.email.split('@')[0].charAt(0).toUpperCase() + 
                     user.email.split('@')[0].slice(1);
    }
    
    // Actualizar elementos
    if (userNameElement) userNameElement.textContent = displayName;
    if (userEmailElement) userEmailElement.textContent = user.email;
    
    // Actualizar avatar con iniciales
    if (userAvatarElement) {
        const initials = getInitials(displayName);
        userAvatarElement.innerHTML = `<span>${initials}</span>`;
    }
}

function getInitials(name) {
    return name
        .split(' ')
        .map(word => word.charAt(0))
        .join('')
        .toUpperCase()
        .substring(0, 2);
}

function setupAuthStateListener() {
    // Manejo de cambios de estado de autenticación
    window.supabaseClient.auth.onAuthStateChange((event, session) => {
        if (event === 'SIGNED_OUT') {
            window.location.href = 'login.html';
        }
        
        if (event === 'TOKEN_REFRESHED') {
            console.log('Token refreshed successfully');
        }
        
        if (event === 'USER_UPDATED') {
            console.log('User updated:', session?.user);
            if (session?.user) {
                updateUserDisplay(session.user);
            }
        }
    });
}

async function logout() {
    try {
        showLoading(true);
        
        const { error } = await window.supabaseClient.auth.signOut();
        
        if (error) {
            throw error;
        }
        
        // Limpiar storage local
        localStorage.removeItem('rememberUser');
        
        // Redirigir a login
        window.location.href = 'login.html';
        
    } catch (error) {
        console.error('Error during logout:', error);
        showNotification('Error al cerrar sesión', 'error');
    } finally {
        showLoading(false);
    }
}

// ==============================================
// NAVEGACIÓN A DASHBOARDS
// ==============================================
function openDashboard(type) {
    console.log('Abriendo dashboard:', type);
    showLoading(true);
    
    // Simular tiempo de carga
    setTimeout(() => {
        const dashboardUrls = window.ILAR_CONFIG.DASHBOARD_URLS;
        
        if (type === 'moleculas') {
            if (dashboardUrls.moleculas) {
                window.open(dashboardUrls.moleculas, '_blank');
                showNotification('Abriendo Dashboard de Moléculas...', 'success');
            } else {
                showNotification('URL de dashboard de moléculas no configurada', 'error');
            }
        } else if (type === 'suplementos') {
            if (dashboardUrls.suplementos) {
                window.open(dashboardUrls.suplementos, '_blank');
                showNotification('Abriendo Dashboard de Suplementos...', 'success');
            } else {
                showNotification('URL de dashboard de suplementos no configurada', 'error');
            }
        } else {
            showNotification('Tipo de dashboard no reconocido', 'error');
        }
        
        showLoading(false);
    }, 1000);
}

// ==============================================
// FUNCIONES DE UI
// ==============================================
function initializeAnimations() {
    // Animación de las tarjetas al hacer scroll
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);
    
    // Observar elementos con animación
    document.querySelectorAll('.dashboard-card, .stat-card, .update-item').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(el);
    });
    
    // Animación de contador para las estadísticas
    animateCounters();
}

function animateCounters() {
    const counters = document.querySelectorAll('.stat-content h3');
    
    counters.forEach(counter => {
        const target = parseInt(counter.textContent.replace(/,/g, ''));
        if (isNaN(target)) return;
        
        const duration = 2000; // 2 segundos
        const step = target / (duration / 16); // 60fps
        let current = 0;
        
        const timer = setInterval(() => {
            current += step;
            if (current >= target) {
                current = target;
                clearInterval(timer);
            }
            
            // Formatear número con comas
            counter.textContent = Math.floor(current).toLocaleString();
        }, 16);
    });
}

function updateLastLogin() {
    const lastLoginElement = document.getElementById('lastLogin');
    if (lastLoginElement) {
        const now = new Date();
        const timeString = now.toLocaleString('es-ES', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
        lastLoginElement.textContent = timeString;
    }
}

function showNotification(message, type = 'info') {
    // Crear elemento de notificación si no existe
    let notification = document.getElementById('notification');
    if (!notification) {
        notification = document.createElement('div');
        notification.id = 'notification';
        notification.className = 'notification';
        document.body.appendChild(notification);
    }
    
    notification.textContent = message;
    notification.className = `notification ${type}`;
    
    // Mostrar notificación
    setTimeout(() => {
        notification.classList.add('show');
    }, 100);
    
    // Ocultar después de 3 segundos
    setTimeout(() => {
        notification.classList.remove('show');
    }, 3000);
}

function showLoading(show) {
    let overlay = document.getElementById('loadingOverlay');
    
    // Crear overlay si no existe
    if (!overlay) {
        overlay = document.createElement('div');
        overlay.id = 'loadingOverlay';
        overlay.className = 'loading-overlay';
        overlay.innerHTML = `
            <div class="loading-content">
                <div class="loading-spinner"></div>
                <p>Cargando dashboard...</p>
            </div>
        `;
        document.body.appendChild(overlay);
    }
    
    if (show) {
        overlay.style.display = 'flex';
    } else {
        overlay.style.display = 'none';
    }
}

// ==============================================
// MANEJO DE ERRORES Y RECONEXIÓN
// ==============================================
window.addEventListener('online', function() {
    showNotification('Conexión restaurada', 'success');
});

window.addEventListener('offline', function() {
    showNotification('Sin conexión a internet', 'warning');
});

// ==============================================
// FUNCIONES ADICIONALES
// ==============================================

// Actualizar estadísticas en tiempo real (opcional)
async function updateStats() {
    try {
        // Aquí podrías hacer llamadas a APIs para obtener estadísticas actualizadas
        // Por ejemplo, contar registros en Supabase o llamar a tu backend
        
    } catch (error) {
        console.error('Error updating stats:', error);
    }
}

// Función para verificar el estado de los dashboards
async function checkDashboardStatus() {
    const dashboards = ['moleculas', 'suplementos'];
    const dashboardUrls = window.ILAR_CONFIG.DASHBOARD_URLS;
    
    for (const dashboard of dashboards) {
        try {
            if (dashboardUrls[dashboard]) {
                const response = await fetch(dashboardUrls[dashboard], { 
                    method: 'GET',
                });
                
                updateDashboardStatus(dashboard, 'online');
            }
        } catch (error) {
            updateDashboardStatus(dashboard, 'offline');
        }
    }
}

function updateDashboardStatus(dashboard, status) {
    const badge = document.querySelector(`.${dashboard}-card .card-badge`);
    if (badge) {
        if (status === 'online') {
            badge.textContent = 'Disponible';
            badge.style.background = 'rgba(76, 175, 80, 0.2)';
            badge.style.color = '#4CAF50';
        } else {
            badge.textContent = 'Offline';
            badge.style.background = 'rgba(244, 67, 54, 0.2)';
            badge.style.color = '#F44336';
        }
    }
}

// ==============================================
// ATAJOS DE TECLADO
// ==============================================
document.addEventListener('keydown', function(e) {
    // Alt + 1: Dashboard Moléculas
    if (e.altKey && e.key === '1') {
        e.preventDefault();
        openDashboard('moleculas');
    }
    
    // Alt + 2: Dashboard Suplementos
    if (e.altKey && e.key === '2') {
        e.preventDefault();
        openDashboard('suplementos');
    }
    
    // Alt + L: Logout
    if (e.altKey && e.key === 'l') {
        e.preventDefault();
        logout();
    }
});

// ==============================================
// INICIALIZACIÓN FINAL
// ==============================================
// Verificar estado de dashboards al cargar
window.addEventListener('load', function() {
    if (window.ILAR_CONFIG && window.ILAR_CONFIG.DASHBOARD_URLS) {
        setTimeout(checkDashboardStatus, 2000);
    }
});