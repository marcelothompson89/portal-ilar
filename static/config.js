// ==============================================
// CONFIGURACIÓN CENTRAL DEL PORTAL ILAR
// ==============================================

// static/config.js

// PRIMERO: Detectar entorno (podés dejarlo si lo usás para otras cosas)
const isProduction = window.location.hostname !== 'localhost' &&
                     window.location.hostname !== '127.0.0.1';

// SEGUNDO: Configuración base
const CONFIG = {
  SUPABASE_URL: 'https://gbrufkofxwdnanmhlgms.supabase.co',
  SUPABASE_ANON_KEY: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdicnVma29meHdkbmFubWhsZ21zIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTUzNTMwMjcsImV4cCI6MjA3MDkyOTAyN30.jb1bzrRTVKawj8kos-XRk-ZAUS7lsJL1JSFjFQKQuFk',

  // 👇 Usar SIEMPRE rutas relativas servidas por FastAPI
  DASHBOARD_URLS: {
    moleculas: '/analytics/molecular-data',
    suplementos: '/analytics/supplement-regulations'
  },

  APP: { name: 'Portal ILAR', version: '1.0.0', author: 'ILAR',
         description: 'Asociación Latinoamericana de Autocuidado Responsable' },

  UI: { NOTIFICATION_DURATION: 3000, LOADING_DELAY: 1000, ANIMATION_DURATION: 600 }
};

// Export global
window.ILAR_CONFIG = {
  SUPABASE_URL: CONFIG.SUPABASE_URL,
  SUPABASE_ANON_KEY: CONFIG.SUPABASE_ANON_KEY,
  DASHBOARD_URLS: CONFIG.DASHBOARD_URLS,
  APP: CONFIG.APP,
  UI: CONFIG.UI,
  isProduction
};

console.log('🧬 Portal ILAR inicializado', CONFIG.DASHBOARD_URLS);
console.log('Entorno:', isProduction ? 'Producción' : 'Desarrollo');
console.log('URLs Dashboard:', CONFIG.DASHBOARD_URLS);