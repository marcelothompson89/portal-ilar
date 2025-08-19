/* ==============================================
   SUPLEMENTOS DASHBOARD - API FUNCTIONS
   Portal ILAR - Funciones de API centralizadas
   ============================================== */

/**
 * Módulo centralizado para todas las llamadas de API
 * del dashboard de suplementos
 */
const SupplementsAPI = {
    // Cache para optimizar llamadas repetidas
    cache: new Map(),
    
    // Configuración base
    config: {
        baseURL: '/api/suplementos',
        timeout: 30000,
        retries: 3
    },

    /**
     * Función base para hacer peticiones HTTP
     * @param {string} endpoint - Endpoint de la API
     * @param {Object} options - Opciones de la petición
     * @returns {Promise} Respuesta de la API
     */
    async request(endpoint, options = {}) {
        const url = `${this.config.baseURL}${endpoint}`;
        const cacheKey = `${url}?${new URLSearchParams(options.params || {})}`;
        
        // Verificar cache si no es POST/PUT/DELETE
        if (!options.method || options.method === 'GET') {
            if (this.cache.has(cacheKey)) {
                const cached = this.cache.get(cacheKey);
                // Cache válido por 5 minutos
                if (Date.now() - cached.timestamp < 300000) {
                    return cached.data;
                }
            }
        }

        try {
            // Construir URL con parámetros
            const searchParams = new URLSearchParams();
            if (options.params) {
                Object.entries(options.params).forEach(([key, value]) => {
                    if (Array.isArray(value)) {
                        value.forEach(v => searchParams.append(key, v));
                    } else if (value !== null && value !== undefined && value !== '') {
                        searchParams.append(key, value);
                    }
                });
            }
            
            const finalURL = searchParams.toString() ? `${url}?${searchParams}` : url;
            
            // Configurar petición
            const requestConfig = {
                method: options.method || 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options.fetchOptions
            };

            if (options.body) {
                requestConfig.body = JSON.stringify(options.body);
            }

            // Realizar petición con timeout
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), this.config.timeout);
            
            const response = await fetch(finalURL, {
                ...requestConfig,
                signal: controller.signal
            });
            
            clearTimeout(timeoutId);

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            
            // Guardar en cache para GET requests
            if (!options.method || options.method === 'GET') {
                this.cache.set(cacheKey, {
                    data,
                    timestamp: Date.now()
                });
            }

            return data;

        } catch (error) {
            console.error(`API Error [${endpoint}]:`, error);
            
            if (error.name === 'AbortError') {
                throw new Error('La petición tardó demasiado tiempo');
            }
            
            throw new Error(`Error de conexión: ${error.message}`);
        }
    },

    /**
     * Helper para construir parámetros de filtros
     * @param {Object} filters - Objeto de filtros
     * @returns {Object} Parámetros listos para la API
     */
    buildFilterParams(filters = {}) {
        const params = {};
        
        if (filters.ingredient && filters.ingredient !== 'all') {
            params.ingredient = filters.ingredient;
        }
        
        if (filters.ingredient_type && filters.ingredient_type !== 'all') {
            params.ingredient_type = filters.ingredient_type;
        }
        
        if (filters.countries && filters.countries.length > 0) {
            params.countries = filters.countries;
        }
        
        return params;
    },

    /**
     * Obtener estadísticas básicas de suplementos
     * @param {Object} filters - Filtros aplicados
     * @returns {Promise} Estadísticas
     */
    async getStats(filters = {}) {
        const params = this.buildFilterParams(filters);
        
        return await this.request('/stats', { params });
    },

    /**
     * Obtener datos de suplementos con paginación
     * @param {Object} options - Opciones de consulta
     * @returns {Promise} Datos paginados
     */
    async getData(options = {}) {
        const { filters = {}, pagination = {} } = options;
        
        const params = {
            ...this.buildFilterParams(filters),
            limit: pagination.limit || 50,
            offset: pagination.offset || 0
        };
        
        return await this.request('/data', { params });
    },

    /**
     * Obtener gráficos para el dashboard
     * @param {Object} filters - Filtros aplicados
     * @returns {Promise} Datos para gráficos
     */
    async getCharts(filters = {}) {
        const params = this.buildFilterParams(filters);
        
        return await this.request('/charts', { params });
    },

    /**
     * Obtener comparación regulatoria entre países
     * @param {Array} countries - Lista de países a comparar
     * @param {Object} options - Opciones adicionales
     * @returns {Promise} Datos de comparación
     */
    async getRegulatoryComparison(countries = [], options = {}) {
        if (!countries || countries.length === 0) {
            throw new Error('Debe seleccionar al menos un país para comparar');
        }

        const params = {
            countries: countries,
            ...options
        };
        
        return await this.request('/comparison', { params });
    },

    /**
     * Obtener secciones regulatorias disponibles
     * @returns {Promise} Secciones disponibles
     */
    async getRegulatorySection() {
        return await this.request('/regulatory-sections');
    },

    /**
     * Obtener estadísticas del marco regulatorio
     * @returns {Promise} Estadísticas regulatorias
     */
    async getRegulatoryStats() {
        return await this.request('/regulatory-stats');
    },

    /**
     * Obtener análisis específico de un ingrediente
     * @param {string} ingredient - Nombre del ingrediente
     * @param {Object} options - Opciones adicionales
     * @returns {Promise} Análisis del ingrediente
     */
    async getIngredientAnalysis(ingredient, options = {}) {
        if (!ingredient) {
            throw new Error('Debe especificar un ingrediente');
        }

        const params = {
            ingredient: ingredient,
            limit: options.limit || 1000,
            ...options
        };
        
        return await this.request('/data', { params });
    },

    /**
     * Limpiar cache (útil cuando se actualizan datos)
     * @param {string} pattern - Patrón para limpiar cache específico
     */
    clearCache(pattern = null) {
        if (!pattern) {
            this.cache.clear();
            console.log('Cache completamente limpiado');
        } else {
            const keysToDelete = [];
            for (const key of this.cache.keys()) {
                if (key.includes(pattern)) {
                    keysToDelete.push(key);
                }
            }
            keysToDelete.forEach(key => this.cache.delete(key));
            console.log(`Cache limpiado para patrón: ${pattern}`);
        }
    },

    /**
     * Verificar estado de la API
     * @returns {Promise} Estado de salud de la API
     */
    async healthCheck() {
        try {
            // Llamada simple para verificar conectividad
            await this.request('/stats');
            return { status: 'healthy', message: 'API funcionando correctamente' };
        } catch (error) {
            return { status: 'error', message: error.message };
        }
    },

    /**
     * Obtener información de países disponibles
     * @returns {Promise} Lista de países con metadatos
     */
    async getAvailableCountries() {
        const stats = await this.getStats();
        return stats.available_countries || [];
    },

    /**
     * Obtener información de ingredientes disponibles
     * @returns {Promise} Lista de ingredientes con metadatos
     */
    async getAvailableIngredients() {
        const stats = await this.getStats();
        return stats.available_ingredients || [];
    },

    /**
     * Obtener tipos de ingredientes disponibles
     * @returns {Promise} Lista de tipos
     */
    async getAvailableTypes() {
        const stats = await this.getStats();
        return stats.available_types || [];
    },

    /**
     * Función helper para manejar errores de manera consistente
     * @param {Error} error - Error capturado
     * @param {string} context - Contexto donde ocurrió el error
     * @returns {Object} Error formateado
     */
    formatError(error, context = 'API') {
        console.error(`[${context}] Error:`, error);
        
        let userMessage = 'Ha ocurrido un error inesperado';
        
        if (error.message.includes('timeout') || error.message.includes('tardó demasiado')) {
            userMessage = 'La conexión tardó demasiado tiempo. Intenta nuevamente.';
        } else if (error.message.includes('404')) {
            userMessage = 'Recurso no encontrado. Verifica la configuración.';
        } else if (error.message.includes('500')) {
            userMessage = 'Error del servidor. Intenta más tarde.';
        } else if (error.message.includes('network') || error.message.includes('fetch')) {
            userMessage = 'Error de conexión. Verifica tu internet.';
        } else if (error.message.includes('JSON')) {
            userMessage = 'Error procesando los datos del servidor.';
        }
        
        return {
            type: 'error',
            message: userMessage,
            technical: error.message,
            context
        };
    },

    /**
     * Reintenta una operación con backoff exponencial
     * @param {Function} operation - Función a reintentar
     * @param {number} maxRetries - Número máximo de reintentos
     * @returns {Promise} Resultado de la operación
     */
    async retryOperation(operation, maxRetries = 3) {
        let lastError;
        
        for (let attempt = 1; attempt <= maxRetries; attempt++) {
            try {
                return await operation();
            } catch (error) {
                lastError = error;
                
                if (attempt === maxRetries) {
                    break;
                }
                
                // Backoff exponencial: 1s, 2s, 4s
                const delay = Math.pow(2, attempt - 1) * 1000;
                console.log(`Intento ${attempt} falló, reintentando en ${delay}ms...`);
                
                await new Promise(resolve => setTimeout(resolve, delay));
            }
        }
        
        throw lastError;
    }
};

// Funciones de conveniencia para uso directo
const SupplementsAPIHelpers = {
    /**
     * Cargar datos iniciales del dashboard
     * @returns {Promise} Datos iniciales completos
     */
    async loadInitialData() {
        try {
            // Cargar estadísticas base
            const stats = await SupplementsAPI.getStats();
            
            // Cargar datos iniciales de la tabla
            const tableData = await SupplementsAPI.getData({
                pagination: { limit: 50, offset: 0 }
            });
            
            return {
                stats,
                tableData,
                success: true
            };
        } catch (error) {
            return {
                error: SupplementsAPI.formatError(error, 'Carga Inicial'),
                success: false
            };
        }
    },

    /**
     * Aplicar filtros y obtener datos actualizados
     * @param {Object} filters - Filtros a aplicar
     * @returns {Promise} Datos filtrados
     */
    async applyFilters(filters) {
        try {
            // Obtener estadísticas con filtros
            const stats = await SupplementsAPI.getStats(filters);
            
            // Obtener datos de tabla con filtros
            const tableData = await SupplementsAPI.getData({
                filters,
                pagination: { limit: 50, offset: 0 }
            });
            
            // Obtener gráficos con filtros
            const charts = await SupplementsAPI.getCharts(filters);
            
            return {
                stats,
                tableData,
                charts,
                success: true
            };
        } catch (error) {
            return {
                error: SupplementsAPI.formatError(error, 'Aplicar Filtros'),
                success: false
            };
        }
    },

    /**
     * Cargar análisis completo de un ingrediente
     * @param {string} ingredient - Ingrediente a analizar
     * @returns {Promise} Análisis completo
     */
    async loadIngredientAnalysis(ingredient) {
        try {
            const data = await SupplementsAPI.getIngredientAnalysis(ingredient);
            
            if (!data.data || data.data.length === 0) {
                throw new Error('No se encontraron datos para este ingrediente');
            }
            
            return {
                ingredient,
                data: data.data,
                success: true
            };
        } catch (error) {
            return {
                error: SupplementsAPI.formatError(error, 'Análisis de Ingrediente'),
                success: false
            };
        }
    },

    /**
     * Cargar comparación regulatoria completa
     * @param {Array} countries - Países a comparar
     * @returns {Promise} Comparación completa
     */
    async loadRegulatoryComparison(countries) {
        try {
            // Obtener comparación
            const comparison = await SupplementsAPI.getRegulatoryComparison(countries);
            
            // Obtener secciones disponibles
            const sections = await SupplementsAPI.getRegulatorySection();
            
            return {
                comparison,
                sections,
                countries,
                success: true
            };
        } catch (error) {
            return {
                error: SupplementsAPI.formatError(error, 'Comparación Regulatoria'),
                success: false
            };
        }
    }
};

// Exportar para uso global
window.SupplementsAPI = SupplementsAPI;
window.SupplementsAPIHelpers = SupplementsAPIHelpers;