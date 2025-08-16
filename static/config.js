// ==============================================
// CONFIGURACIÓN CENTRAL DEL PORTAL ILAR
// ==============================================

// PRIMERO: Detectar entorno
const isProduction = window.location.hostname !== 'localhost' && 
                    window.location.hostname !== '127.0.0.1';

// SEGUNDO: Configuración base
const CONFIG = {
    // Credenciales de Supabase - REEMPLAZA CON TUS CREDENCIALES REALES
    SUPABASE_URL: 'https://gbrufkofxwdnanmhlgms.supabase.co',
    SUPABASE_ANON_KEY: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdicnVma29meHdkbmFubWhsZ21zIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTUzNTMwMjcsImV4cCI6MjA3MDkyOTAyN30.jb1bzrRTVKawj8kos-XRk-ZAUS7lsJL1JSFjFQKQuFk',
    
    // URLs de los dashboards que se ajustan según el entorno
    DASHBOARD_URLS: isProduction ? {
        moleculas: window.location.origin + '/analytics/molecular-data',
        suplementos: window.location.origin + '/analytics/supplement-regulations'
    } : {
        moleculas: 'http://localhost:8502',
        suplementos: 'http://localhost:8503'
    },
    
    // Información de la aplicación
    APP: {
        name: 'Portal ILAR',
        version: '1.0.0',
        author: 'ILAR',
        description: 'Asociación Latinoamericana de Autocuidado Responsable'
    },
    
    // Configuración de UI
    UI: {
        NOTIFICATION_DURATION: 3000, // 3 segundos
        LOADING_DELAY: 1000, // 1 segundo
        ANIMATION_DURATION: 600 // 0.6 segundos
    }
};

// TERCERO: Exportar configuración global
window.ILAR_CONFIG = {
    SUPABASE_URL: CONFIG.SUPABASE_URL,
    SUPABASE_ANON_KEY: CONFIG.SUPABASE_ANON_KEY,
    DASHBOARD_URLS: CONFIG.DASHBOARD_URLS,
    APP: CONFIG.APP,
    UI: CONFIG.UI,
    isProduction: isProduction
};

// Debug info
console.log('🧬 Portal ILAR inicializado');
console.log('Entorno:', isProduction ? 'Producción' : 'Desarrollo');
console.log('URLs Dashboard:', CONFIG.DASHBOARD_URLS);