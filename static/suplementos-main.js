/* ==============================================
   SUPLEMENTOS DASHBOARD - MAIN LOGIC
   Portal ILAR - Lógica principal y orchestración
   ============================================== */

/**
 * Dashboard principal de suplementos
 * Orchesta todos los componentes y maneja el estado global
 */
const SupplementsDashboard = {
    // Estado global de la aplicación
    state: {
        currentFilters: {
            ingredient: 'all',
            ingredient_type: 'all',
            countries: []
        },
        currentData: {
            data: [],
            pagination: {
                total: 0,
                limit: 50,
                offset: 0,
                has_next: false
            }
        },
        allColumns: [],
        selectedColumns: ['pais', 'ingrediente', 'tipo', 'minimo', 'maximo', 'unidad', 'establecido'],
        availableData: {
            countries: [],
            ingredients: [],
            types: []
        },
        currentSection: 'datos',
        isLoading: false
    },

    /**
     * Inicializar el dashboard
     */
    async init() {
        try {
            this.updateLoadingStep('Inicializando interfaz...');
            
            // Configurar navegación del sidebar
            this.initializeSidebar();
            
            // Configurar event listeners
            this.setupEventListeners();
            
            // Cargar datos iniciales
            this.updateLoadingStep('Cargando datos de suplementos...');
            await this.loadInitialData();
            
            this.updateLoadingStep('¡Listo!');
            
            // Ocultar loading screen
            setTimeout(() => {
                this.hideInitialLoading();
            }, 500);
            
        } catch (error) {
            console.error('Error inicializando dashboard:', error);
            this.updateLoadingStep('Error cargando datos');
            SupplementsComponents.notifications.error('Error cargando los datos. Por favor, recarga la página.');
            
            setTimeout(() => {
                this.hideInitialLoading();
            }, 2000);
        }
    },

    /**
     * Actualizar mensaje de loading
     */
    updateLoadingStep(message) {
        const loadingSteps = document.getElementById('loadingSteps');
        if (loadingSteps) {
            loadingSteps.textContent = message;
        }
    },

    /**
     * Ocultar pantalla de loading inicial
     */
    hideInitialLoading() {
        const loadingScreen = document.getElementById('initialLoading');
        if (loadingScreen) {
            loadingScreen.classList.add('hidden');
        }
    },

    /**
     * Configurar navegación del sidebar
     */
    initializeSidebar() {
        const menuLinks = document.querySelectorAll('.menu-link');
        const contentSections = document.querySelectorAll('.content-section');

        menuLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                
                const section = link.getAttribute('data-section');
                this.switchSection(section);
                
                // Actualizar UI del sidebar
                menuLinks.forEach(l => l.classList.remove('active'));
                link.classList.add('active');
                
                // Mostrar sección correspondiente
                contentSections.forEach(s => s.classList.remove('active'));
                const targetSection = document.getElementById(`section-${section}`);
                if (targetSection) {
                    targetSection.classList.add('active');
                }
            });
        });
    },

    /**
     * Configurar event listeners globales
     */
    setupEventListeners() {
        // Cambios en filtros de países
        window.addEventListener('countriesChanged', (e) => {
            this.state.currentFilters.countries = e.detail.countries;
        });

        // Resize de ventana para gráficos
        window.addEventListener('resize', this.utils.debounce(() => {
            this.charts.resizeAll();
        }, 250));

        // Selector de ingrediente para análisis
        const ingredientAnalysisSelect = document.getElementById('ingredientAnalysisSelect');
        if (ingredientAnalysisSelect) {
            ingredientAnalysisSelect.addEventListener('change', (e) => {
                this.ingredient.loadAnalysis(e.target.value);
            });
        }
    },

    /**
     * Cambiar sección activa
     */
    async switchSection(section) {
        this.state.currentSection = section;
        
        switch(section) {
            case 'datos':
                // Datos ya están cargados
                break;
            case 'analisis':
                await this.charts.loadAll();
                break;
            case 'ingrediente':
                // El análisis se carga cuando se selecciona un ingrediente
                break;
            case 'comparacion':
                // La comparación se carga cuando se seleccionan países
                break;
        }
    },

    /**
     * Cargar datos iniciales
     */
    async loadInitialData() {
        try {
            this.updateLoadingStep('Conectando con el servidor...');
            
            const result = await SupplementsAPIHelpers.loadInitialData();
            
            if (!result.success) {
                throw new Error(result.error.message);
            }
            
            this.updateLoadingStep('Procesando datos...');
            
            // Actualizar estado
            this.state.currentData = result.tableData;
            this.state.availableData = {
                countries: result.stats.available_countries || [],
                ingredients: result.stats.available_ingredients || [],
                types: result.stats.available_types || []
            };
            
            if (result.tableData.data && result.tableData.data.length > 0) {
                this.state.allColumns = Object.keys(result.tableData.data[0]);
            }
            
            this.updateLoadingStep('Configurando filtros...');
            
            // Configurar UI
            this.setupFilters(result.stats);
            this.updateStats(result.stats);
            this.table.render();
            
            this.updateLoadingStep('Generando gráficos...');
            await this.charts.loadAll();
            
        } catch (error) {
            console.error('Error cargando datos iniciales:', error);
            throw error;
        }
    },

    /**
     * Configurar filtros iniciales
     */
    setupFilters(stats) {
        // Poblar selectores
        SupplementsComponents.filters.populateSelect(
            'ingredientSelect', 
            stats.available_ingredients, 
            'Todos los ingredientes'
        );
        
        SupplementsComponents.filters.populateSelect(
            'typeSelect', 
            stats.available_types, 
            'Todos los tipos'
        );
        
        SupplementsComponents.filters.populateSelect(
            'ingredientAnalysisSelect', 
            stats.available_ingredients, 
            'Selecciona un ingrediente...'
        );
        
        // Configurar selector múltiple de países
        SupplementsComponents.filters.createCountryMultiSelect(stats.available_countries);
        
        // Configurar selector de columnas
        this.table.updateColumnSelector();
    },

    /**
     * Actualizar estadísticas
     */
    updateStats(data) {
        SupplementsComponents.stats.update(data);
    },

    /**
     * Módulo de filtros
     */
    filters: {
        /**
         * Aplicar filtros
         */
        async apply() {
            try {
                SupplementsComponents.loading.showGlobal('Aplicando filtros...');
                
                // Obtener filtros actuales
                const filters = SupplementsComponents.filters.getCurrentFilters();
                SupplementsDashboard.state.currentFilters = filters;
                
                // Aplicar filtros via API
                const result = await SupplementsAPIHelpers.applyFilters(filters);
                
                if (!result.success) {
                    throw new Error(result.error.message);
                }
                
                // Actualizar estado y UI
                SupplementsDashboard.state.currentData = result.tableData;
                SupplementsDashboard.updateStats(result.stats);
                SupplementsDashboard.table.render();
                
                // Recargar gráficos si estamos en esa sección
                if (SupplementsDashboard.state.currentSection === 'analisis') {
                    await SupplementsDashboard.charts.loadAll();
                }
                
                SupplementsComponents.loading.hideGlobal();
                SupplementsComponents.notifications.success('Filtros aplicados correctamente');
                
            } catch (error) {
                console.error('Error aplicando filtros:', error);
                SupplementsComponents.loading.hideGlobal();
                SupplementsComponents.notifications.error('Error aplicando los filtros.');
            }
        },

        /**
         * Limpiar filtros
         */
        async clear() {
            try {
                SupplementsComponents.filters.clear();
                
                // Resetear estado
                SupplementsDashboard.state.currentFilters = {
                    ingredient: 'all',
                    ingredient_type: 'all',
                    countries: []
                };
                
                // Recargar datos
                await SupplementsDashboard.loadInitialData();
                SupplementsComponents.notifications.success('Filtros limpiados correctamente');
                
            } catch (error) {
                console.error('Error limpiando filtros:', error);
                SupplementsComponents.notifications.error('Error limpiando los filtros.');
            }
        }
    },

    /**
     * Módulo de tabla
     */
    table: {
        /**
         * Renderizar tabla
         */
        render() {
            const { data, pagination } = SupplementsDashboard.state.currentData;
            const columns = SupplementsDashboard.state.selectedColumns.map(col => ({
                key: col,
                label: col,
                formatter: (value, row) => {
                    if (col === 'establecido') {
                        return SupplementsComponents.utils.formatBoolean(value);
                    }
                    return value === null || value === undefined ? '-' : value;
                }
            }));

            // Mostrar información de registros
            this.showDataInfo();

            // Renderizar tabla
            SupplementsComponents.table.render({
                target: document.querySelector('.table-container'),
                data: data || [],
                columns: columns,
                pagination: pagination,
                onPageChange: (offset) => this.goToPage(offset),
                emptyMessage: 'No hay datos para mostrar con los filtros actuales.'
            });
        },

        /**
         * Mostrar información de datos
         */
        showDataInfo() {
            const dataInfo = document.getElementById('dataInfo');
            if (!dataInfo) return;

            const { total, offset, limit } = SupplementsDashboard.state.currentData.pagination;
            const dataLength = SupplementsDashboard.state.currentData.data?.length || 0;
            
            if (dataLength === 0) {
                dataInfo.innerHTML = '<div class="info-message">No hay datos para mostrar con los filtros actuales.</div>';
                return;
            }

            if (SupplementsDashboard.state.selectedColumns.length === 0) {
                dataInfo.innerHTML = '<div class="error-message show">Selecciona al menos una columna para mostrar.</div>';
                return;
            }

            const startRecord = offset + 1;
            const endRecord = Math.min(offset + dataLength, total);
            
            dataInfo.innerHTML = `
                <div class="info-message">
                    <i class="fas fa-info-circle"></i>
                    Mostrando registros ${startRecord} - ${endRecord} de ${total.toLocaleString()} total
                </div>
            `;
        },

        /**
         * Ir a página específica
         */
        async goToPage(newOffset) {
            try {
                SupplementsComponents.loading.show('.table-container', 'Cargando página...');
                
                const result = await SupplementsAPI.getData({
                    filters: SupplementsDashboard.state.currentFilters,
                    pagination: { 
                        limit: SupplementsDashboard.state.currentData.pagination.limit, 
                        offset: newOffset 
                    }
                });
                
                SupplementsDashboard.state.currentData = result;
                this.render();
                
            } catch (error) {
                console.error('Error cargando página:', error);
                SupplementsComponents.notifications.error('Error cargando la página.');
            }
        },

        /**
         * Actualizar selector de columnas
         */
        updateColumnSelector() {
            const select = document.getElementById('columnSelect');
            if (!select) return;

            select.innerHTML = '';
            
            SupplementsDashboard.state.allColumns.forEach(col => {
                const opt = document.createElement('option');
                opt.value = col;
                opt.textContent = col;
                if (SupplementsDashboard.state.selectedColumns.includes(col)) {
                    opt.selected = true;
                }
                select.appendChild(opt);
            });
        },

        /**
         * Aplicar selección de columnas
         */
        applyColumns() {
            const select = document.getElementById('columnSelect');
            if (!select) return;

            SupplementsDashboard.state.selectedColumns = Array.from(select.selectedOptions).map(o => o.value);
            this.render();
        },

        /**
         * Resetear columnas por defecto
         */
        resetColumns() {
            SupplementsDashboard.state.selectedColumns = [
                'pais', 'ingrediente', 'tipo', 'minimo', 'maximo', 'unidad', 'establecido'
            ].filter(col => SupplementsDashboard.state.allColumns.includes(col));
            
            this.updateColumnSelector();
            this.render();
        }
    },

    /**
     * Módulo de gráficos
     */
    charts: {
        /**
         * Cargar todos los gráficos
         */
        async loadAll() {
            try {
                const chartIds = [
                    'chart-ingredients-country',
                    'chart-type-distribution', 
                    'chart-regulation-status',
                    'chart-top-ingredients'
                ];

                // Mostrar loading en todos los gráficos
                chartIds.forEach(id => {
                    SupplementsComponents.loading.show(`#${id}`, 'Cargando gráfico...');
                });

                // Obtener datos de gráficos
                const charts = await SupplementsAPI.getCharts(SupplementsDashboard.state.currentFilters);

                // Renderizar cada gráfico
                SupplementsComponents.charts.render('chart-ingredients-country', charts.ingredients_by_country);
                SupplementsComponents.charts.render('chart-type-distribution', charts.type_distribution);
                SupplementsComponents.charts.render('chart-regulation-status', charts.regulation_status);
                SupplementsComponents.charts.render('chart-top-ingredients', charts.top_ingredients);

            } catch (error) {
                console.error('Error cargando gráficos:', error);
                
                // Mostrar error en todos los gráficos
                const chartIds = [
                    'chart-ingredients-country',
                    'chart-type-distribution', 
                    'chart-regulation-status',
                    'chart-top-ingredients'
                ];
                
                chartIds.forEach(id => {
                    SupplementsComponents.charts.showError(id, 'Error cargando gráfico');
                });
            }
        },

        /**
         * Redimensionar todos los gráficos
         */
        resizeAll() {
            const chartIds = [
                'chart-ingredients-country',
                'chart-type-distribution', 
                'chart-regulation-status',
                'chart-top-ingredients',
                'ingredient-range-chart'
            ];
            
            chartIds.forEach(id => {
                const element = document.getElementById(id);
                if (element && element.data) {
                    try {
                        Plotly.Plots.resize(id);
                    } catch (error) {
                        console.warn(`Error redimensionando gráfico ${id}:`, error);
                    }
                }
            });
        }
    },

    /**
     * Módulo de análisis de ingredientes
     */
    ingredient: {
        /**
         * Cargar análisis de ingrediente
         */
        async loadAnalysis(ingredient) {
            const detailsDiv = document.getElementById('ingredientDetails');
            
            if (!ingredient) {
                detailsDiv.classList.add('hidden');
                return;
            }
            
            try {
                detailsDiv.classList.remove('hidden');
                SupplementsComponents.loading.show('#ingredient-range-chart', 'Cargando análisis...');
                
                // Cargar datos del ingrediente
                const result = await SupplementsAPIHelpers.loadIngredientAnalysis(ingredient);
                
                if (!result.success) {
                    throw new Error(result.error.message);
                }
                
                const ingredientData = result.data;
                const firstRecord = ingredientData[0];
                
                // Actualizar estadísticas
                this.updateStats(ingredientData, firstRecord);
                
                // Crear gráfico de rangos
                this.createRangeChart(ingredientData, ingredient);
                
                // Crear tabla detallada
                this.createTable(ingredientData);
                
            } catch (error) {
                console.error('Error cargando análisis de ingrediente:', error);
                SupplementsComponents.notifications.error('Error cargando el análisis del ingrediente.');
                detailsDiv.classList.add('hidden');
            }
        },

        /**
         * Actualizar estadísticas del ingrediente
         */
        updateStats(data, firstRecord) {
            const establishedCount = data.filter(d => d.establecido).length;
            const minValues = data.filter(d => d.minimo !== null).map(d => d.minimo);
            const maxValues = data.filter(d => d.maximo !== null).map(d => d.maximo);
            
            document.getElementById('ingredientCountries').textContent = `${establishedCount}/${data.length}`;
            document.getElementById('ingredientType').textContent = firstRecord.tipo || '-';
            document.getElementById('ingredientUnit').textContent = firstRecord.unidad || '-';
            
            if (minValues.length > 0 && maxValues.length > 0) {
                const globalMin = Math.min(...minValues);
                const globalMax = Math.max(...maxValues);
                document.getElementById('ingredientRange').textContent = 
                    `${SupplementsComponents.utils.formatNumber(globalMin)} - ${SupplementsComponents.utils.formatNumber(globalMax)}`;
            } else {
                document.getElementById('ingredientRange').textContent = 'N/A';
            }
        },

        /**
         * Crear gráfico de rangos
         */
        createRangeChart(data, ingredient) {
            const establishedData = data.filter(d => d.establecido && d.minimo !== null && d.maximo !== null);
            
            if (establishedData.length === 0) {
                document.getElementById('ingredient-range-chart').innerHTML = 
                    '<div style="text-align:center; color:var(--text-secondary); padding:2rem;">No hay datos de rangos para mostrar</div>';
                return;
            }
            
            const traces = establishedData.map(d => ({
                x: [d.minimo, d.maximo],
                y: [d.pais, d.pais],
                mode: 'lines+markers',
                name: d.pais,
                line: { width: 6 },
                marker: { size: 8 },
                showlegend: false,
                hovertemplate: `<b>${d.pais}</b><br>Rango: ${d.minimo} - ${d.maximo} ${d.unidad}<extra></extra>`
            }));
            
            const layout = {
                title: `Comparación de Rangos: ${ingredient}`,
                xaxis: { title: `Valores (${establishedData[0].unidad})` },
                yaxis: { title: 'País' },
                height: 400
            };
            
            Plotly.newPlot('ingredient-range-chart', traces, layout, {responsive: true});
        },

        /**
         * Crear tabla de ingrediente
         */
        // suplementos-main.js  (módulo ingredient)
        createTable(data) {
            const columns = [
            { key: 'pais', label: 'País' },
            { key: 'minimo', label: 'Mínimo', formatter: (v) => SupplementsComponents.utils.formatNumber(v) },
            { key: 'maximo', label: 'Máximo', formatter: (v) => SupplementsComponents.utils.formatNumber(v) },
            { key: 'establecido', label: 'Establecido', formatter: (v) => SupplementsComponents.utils.formatBoolean(v) },
            { key: 'categoria_regulacion', label: 'Categoría' },
            { key: 'referencias', label: 'Referencias' }
            ];
        
            // Intento 1: la tabla (si existe)
            const tableEl = document.getElementById('ingredientTable');
            // Intento 2: el contenedor directo de la tabla
            const fallbackContainer = document.querySelector('#section-ingrediente .table-container');
            // Intento 3: el contenedor general de la sección
            const details = document.getElementById('ingredientDetails');
        
            const target =
                (tableEl && tableEl.parentElement) ||
                fallbackContainer ||
                details;
        
            if (!target) {
                console.warn('No se encontró un contenedor para la tabla de ingrediente.');
                return;
            }
        
            SupplementsComponents.table.render({
                target,
                data,
                columns
            });
        }
  
    },

    /**
     * Módulo de comparación regulatoria
     */
    comparison: {
        /**
         * Cargar comparación regulatoria
         */
        async load() {
            try {
                const select = document.getElementById('comparisonCountries');
                const selectedCountries = Array.from(select.selectedOptions).map(option => option.value);
                
                if (selectedCountries.length === 0) {
                    SupplementsComponents.notifications.error('Selecciona al menos un país para comparar');
                    return;
                }
                
                SupplementsComponents.loading.showGlobal('Cargando comparación regulatoria...');
                
                // Cargar datos de comparación
                const result = await SupplementsAPIHelpers.loadRegulatoryComparison(selectedCountries);
                
                if (!result.success) {
                    throw new Error(result.error.message);
                }
                
                // Renderizar tabla de comparación
                SupplementsComponents.regulatoryComparison.renderTable(
                    result.comparison.data || result.comparison, 
                    selectedCountries
                );
                
                SupplementsComponents.loading.hideGlobal();
                SupplementsComponents.notifications.success('Comparación cargada correctamente');
                
            } catch (error) {
                console.error('Error cargando comparación regulatoria:', error);
                SupplementsComponents.loading.hideGlobal();
                SupplementsComponents.notifications.error('Error cargando la comparación regulatoria.');
            }
        }
    },

    /**
     * Utilidades del dashboard
     */
    utils: {
        /**
         * Debounce function
         */
        debounce(func, delay) {
            return SupplementsComponents.utils.debounce(func, delay);
        },

        /**
         * Verificar estado de la aplicación
         */
        async healthCheck() {
            try {
                const health = await SupplementsAPI.healthCheck();
                if (health.status === 'healthy') {
                    SupplementsComponents.notifications.success('Conexión con el servidor OK');
                } else {
                    SupplementsComponents.notifications.warning('Problemas de conexión detectados');
                }
                return health;
            } catch (error) {
                SupplementsComponents.notifications.error('No se puede conectar con el servidor');
                return { status: 'error', message: error.message };
            }
        },

        /**
         * Limpiar cache y recargar
         */
        async refresh() {
            try {
                SupplementsAPI.clearCache();
                SupplementsComponents.notifications.info('Recargando datos...');
                await SupplementsDashboard.loadInitialData();
                SupplementsComponents.notifications.success('Datos actualizados');
            } catch (error) {
                SupplementsComponents.notifications.error('Error actualizando datos');
            }
        }
    }
};

// Exportar para uso global
window.SupplementsDashboard = SupplementsDashboard;

// Auto-inicialización si ya está el DOM listo
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        SupplementsDashboard.init();
    });
} else {
    SupplementsDashboard.init();
}