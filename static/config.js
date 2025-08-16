// ==============================================
// CONFIGURACIÓN CENTRAL DEL PORTAL ILAR
// ==============================================

// ⚠️ IMPORTANTE: Reemplaza estas credenciales con las tuyas reales
const CONFIG = {
    // Credenciales de Supabase
    SUPABASE_URL: 'https://gbrufkofxwdnanmhlgms.supabase.co',
    SUPABASE_ANON_KEY: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdicnVma29meHdkbmFubWhsZ21zIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTUzNTMwMjcsImV4cCI6MjA3MDkyOTAyN30.jb1bzrRTVKawj8kos-XRk-ZAUS7lsJL1JSFjFQKQuFk",
    
    // URLs ofuscadas que no revelan que son dashboards
    DASHBOARD_URLS: isProduction ? {
        moleculas: window.location.origin + '/analytics/molecular-data',
        suplementos: window.location.origin + '/analytics/supplement-regulations'
    } : {
        moleculas: 'http://localhost:8502',
        suplementos: 'http://localhost:8503'
    },
    
    // Configuración de la aplicación
    APP: {
        name: 'Portal ILAR',
        version: '1.0.0',
        author: 'ILAR',
        description: 'Asociación Latinoamericana de Autocuidado Responsable'
    },
    
    // URLs de producción (cambiar cuando deploys)
    PRODUCTION: {
        WEB_URL: 'https://portal.infoilar.org',
        DASHBOARD_URLS: {
            moleculas: 'https://portal.infoilar.org/moleculas',
            suplementos: 'https://portal.infoilar.org/suplementos'
        }
    },
    
    // Configuración de UI
    UI: {
        NOTIFICATION_DURATION: 3000, // 3 segundos
        LOADING_DELAY: 1000, // 1 segundo
        ANIMATION_DURATION: 600 // 0.6 segundos
    }
};

// Detectar si estamos en producción o desarrollo
const isProduction = window.location.hostname !== 'localhost' && 
                    window.location.hostname !== '127.0.0.1';

// Usar URLs apropiadas según el entorno
const SUPABASE_URL = CONFIG.SUPABASE_URL;
const SUPABASE_ANON_KEY = CONFIG.SUPABASE_ANON_KEY;
const DASHBOARD_URLS = isProduction ? CONFIG.PRODUCTION.DASHBOARD_URLS : CONFIG.DASHBOARD_URLS;

// Exportar configuración para otros archivos
window.ILAR_CONFIG = {
    SUPABASE_URL: CONFIG.SUPABASE_URL,
    SUPABASE_ANON_KEY: CONFIG.SUPABASE_ANON_KEY,
    DASHBOARD_URLS: CONFIG.DASHBOARD_URLS,
    isProduction
};

console.log('🧬 Portal ILAR inicializado');
console.log('Entorno:', isProduction ? 'Producción' : 'Desarrollo');