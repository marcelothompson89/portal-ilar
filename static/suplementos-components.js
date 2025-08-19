/* ==============================================
   SUPLEMENTOS DASHBOARD - COMPONENTS
   Portal ILAR - Componentes reutilizables
   ============================================== */

/**
 * Módulo de componentes reutilizables para el dashboard de suplementos
 */
const SupplementsComponents = {
    
    /**
     * Componente de notificaciones
     */
    notifications: {
        /**
         * Mostrar notificación
         * @param {string} message - Mensaje a mostrar
         * @param {string} type - Tipo: success, error, warning, info
         * @param {number} duration - Duración en ms (default: 5000)
         */
        show(message, type = 'info', duration = 5000) {
            // Verificar que el mensaje sea válido
            if (!message || typeof message !== 'string') {
                console.error('Error: mensaje de notificación inválido:', message);
                return;
            }
            
            // Crear elemento de notificación
            const notification = document.createElement('div');
            notification.className = `notification notification-${type}`;
            notification.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                padding: 1rem 2rem;
                border-radius: 8px;
                color: white;
                font-weight: 600;
                z-index: 2000;
                box-shadow: 0 4px 12px rgba(0,0,0,0.3);
                animation: slideIn 0.3s ease;
                max-width: 400px;
                word-wrap: break-word;
            `;
            
            // Configurar colores según el tipo
            const colors = {
                success: '#27ae60',
                error: '#e74c3c',
                warning: '#f39c12',
                info: '#3498db'
            };
            
            const icons = {
                success: 'check-circle',
                error: 'exclamation-triangle',
                warning: 'exclamation-circle',
                info: 'info-circle'
            };
            
            notification.style.background = colors[type] || colors.info;
            
            notification.innerHTML = `
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                    <i class="fas fa-${icons[type] || icons.info}"></i>
                    <span>${message}</span>
                    <button onclick="this.parentElement.parentElement.remove()" style="
                        background: none;
                        border: none;
                        color: white;
                        margin-left: auto;
                        cursor: pointer;
                        font-size: 1.2rem;
                        padding: 0 0.5rem;
                    ">&times;</button>
                </div>
            `;
            
            document.body.appendChild(notification);
            
            // Auto-remove después del tiempo especificado
            setTimeout(() => {
                if (notification.parentElement) {
                    notification.style.animation = 'slideOut 0.3s ease';
                    setTimeout(() => notification.remove(), 300);
                }
            }, duration);
        },

        success(message, duration) {
            this.show(message, 'success', duration);
        },

        error(message, duration) {
            this.show(message, 'error', duration);
        },

        warning(message, duration) {
            this.show(message, 'warning', duration);
        },

        info(message, duration) {
            this.show(message, 'info', duration);
        }
    },

    /**
     * Componente de loading
     */
    loading: {
        /**
         * Mostrar loading en un elemento específico
         * @param {string|Element} target - Selector o elemento
         * @param {string} message - Mensaje de loading
         */
        show(target, message = 'Cargando...') {
            const element = typeof target === 'string' ? document.querySelector(target) : target;
            if (!element) return;

            element.innerHTML = `
                <div class="loading-container" style="
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 400px;
                    font-size: 1.1rem;
                    color: var(--text-secondary);
                    flex-direction: column;
                    gap: 1rem;
                ">
                    <div class="loading-spinner"></div>
                    <span>${message}</span>
                </div>
            `;
        },

        /**
         * Ocultar loading y mostrar contenido
         * @param {string|Element} target - Selector o elemento
         * @param {string} content - Contenido a mostrar
         */
        hide(target, content = '') {
            const element = typeof target === 'string' ? document.querySelector(target) : target;
            if (!element) return;

            element.innerHTML = content;
        },

        /**
         * Mostrar loading global
         * @param {string} message - Mensaje de loading
         */
        showGlobal(message = 'Procesando...') {
            let overlay = document.getElementById('globalLoadingOverlay');
            
            if (!overlay) {
                overlay = document.createElement('div');
                overlay.id = 'globalLoadingOverlay';
                overlay.className = 'loading-overlay';
                overlay.style.cssText = `
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    background: rgba(0, 0, 0, 0.7);
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    z-index: 10000;
                `;
                
                overlay.innerHTML = `
                    <div style="
                        background: white;
                        padding: 2rem;
                        border-radius: 15px;
                        text-align: center;
                        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
                    ">
                        <div class="loading-spinner" style="margin-bottom: 1rem;"></div>
                        <p style="color: var(--text-primary); font-weight: 600;">${message}</p>
                    </div>
                `;
                
                document.body.appendChild(overlay);
            } else {
                overlay.style.display = 'flex';
                overlay.querySelector('p').textContent = message;
            }
        },

        /**
         * Ocultar loading global
         */
        hideGlobal() {
            const overlay = document.getElementById('globalLoadingOverlay');
            if (overlay) {
                overlay.style.display = 'none';
            }
        }
    },

    /**
     * Componente de tabla
     */
    table: {
        /**
         * Renderizar tabla con datos
         * @param {Object} config - Configuración de la tabla
         */
        render(config) {
            const {
                target,
                data,
                columns,
                pagination,
                onPageChange,
                emptyMessage = 'No hay datos para mostrar'
            } = config;

            const container = typeof target === 'string' ? document.querySelector(target) : target;
            if (!container) return;

            if (!data || data.length === 0) {
                container.innerHTML = `<div class="info-message">${emptyMessage}</div>`;
                return;
            }

            if (!columns || columns.length === 0) {
                container.innerHTML = '<div class="error-message show">No hay columnas seleccionadas para mostrar.</div>';
                return;
            }

            // Crear tabla
            const table = document.createElement('table');
            table.className = 'data-table';

            // Header
            const thead = document.createElement('thead');
            const headerRow = document.createElement('tr');
            columns.forEach(col => {
                const th = document.createElement('th');
                th.textContent = col.label || col.key;
                headerRow.appendChild(th);
            });
            thead.appendChild(headerRow);
            table.appendChild(thead);

            // Body
            const tbody = document.createElement('tbody');
            data.forEach(row => {
                const tr = document.createElement('tr');
                columns.forEach(col => {
                    const td = document.createElement('td');
                    let value = row[col.key];
                    
                    // Formatear valor si hay formatter
                    if (col.formatter && typeof col.formatter === 'function') {
                        value = col.formatter(value, row);
                    } else if (value === null || value === undefined) {
                        value = '-';
                    }
                    
                    td.innerHTML = value;
                    tr.appendChild(td);
                });
                tbody.appendChild(tr);
            });
            table.appendChild(tbody);

            container.innerHTML = '';
            container.appendChild(table);

            // Agregar paginación si está configurada
            if (pagination) {
                const paginationEl = this.renderPagination(pagination, onPageChange);
                container.appendChild(paginationEl);
            }
        },

        /**
         * Renderizar paginación
         * @param {Object} pagination - Configuración de paginación
         * @param {Function} onPageChange - Callback para cambio de página
         */
        renderPagination(pagination, onPageChange) {
            const { total, offset, limit, has_next } = pagination;
            
            if (total <= limit) {
                return document.createElement('div'); // Elemento vacío
            }

            const paginationDiv = document.createElement('div');
            paginationDiv.className = 'pagination';

            const currentPage = Math.floor(offset / limit) + 1;
            const totalPages = Math.ceil(total / limit);
            const hasPrev = offset > 0;

            paginationDiv.innerHTML = `
                <button ${!hasPrev ? 'disabled' : ''} data-offset="0">
                    <i class="fas fa-angle-double-left"></i> Primera
                </button>
                <button ${!hasPrev ? 'disabled' : ''} data-offset="${offset - limit}">
                    <i class="fas fa-angle-left"></i> Anterior
                </button>
                <span class="current-page">Página ${currentPage} de ${totalPages}</span>
                <button ${!has_next ? 'disabled' : ''} data-offset="${offset + limit}">
                    Siguiente <i class="fas fa-angle-right"></i>
                </button>
                <button ${!has_next ? 'disabled' : ''} data-offset="${(totalPages - 1) * limit}">
                    Última <i class="fas fa-angle-double-right"></i>
                </button>
            `;

            // Agregar event listeners
            paginationDiv.addEventListener('click', (e) => {
                if (e.target.tagName === 'BUTTON' && !e.target.disabled && onPageChange) {
                    const newOffset = parseInt(e.target.getAttribute('data-offset'));
                    onPageChange(newOffset);
                }
            });

            return paginationDiv;
        }
    },

    /**
     * Componente de estadísticas
     */
    stats: {
        /**
         * Actualizar tarjetas de estadísticas
         * @param {Object} data - Datos de estadísticas
         */
        update(data) {
            const updates = {
                totalRecords: data.total_records?.toLocaleString() || '-',
                uniqueCountries: data.unique_countries || '-',
                uniqueIngredients: data.unique_ingredients || '-',
                establishedPercentage: `${Math.round(data.established_percentage || 0)}%`
            };

            Object.entries(updates).forEach(([id, value]) => {
                const element = document.getElementById(id);
                if (element) {
                    this.animateValue(element, value);
                }
            });
        },

        /**
         * Animar cambio de valor en una tarjeta
         * @param {Element} element - Elemento a animar
         * @param {string} newValue - Nuevo valor
         */
        animateValue(element, newValue) {
            element.style.opacity = '0.5';
            setTimeout(() => {
                element.textContent = newValue;
                element.style.opacity = '1';
            }, 150);
        }
    },

    /**
     * Componente de filtros
     */
    filters: {
        /**
         * Poblar selector con opciones
         * @param {string} selectId - ID del selector
         * @param {Array} options - Opciones disponibles
         * @param {string} placeholder - Placeholder para la primera opción
         */
        populateSelect(selectId, options, placeholder = 'Todos') {
            const select = document.getElementById(selectId);
            if (!select) return;

            // Mantener valor actual si existe
            const currentValue = select.value;

            select.innerHTML = `<option value="all">${placeholder}</option>`;
            
            if (options && options.length > 0) {
                options.forEach(option => {
                    const optionEl = document.createElement('option');
                    optionEl.value = option;
                    optionEl.textContent = option;
                    if (option === currentValue) {
                        optionEl.selected = true;
                    }
                    select.appendChild(optionEl);
                });
            }
        },

        /**
         * Crear selector múltiple de países
         * @param {Array} countries - Lista de países
         */
        createCountryMultiSelect(countries) {
            const dropdown = document.getElementById('countryDropdown');
            if (!dropdown) return;

            dropdown.innerHTML = '';
            
            if (!countries || countries.length === 0) {
                dropdown.innerHTML = '<div class="country-option" style="font-style: italic; color: #888;">No hay países disponibles</div>';
                return;
            }
            
            countries.forEach(country => {
                const option = document.createElement('div');
                option.className = 'country-option';
                
                const checkbox = document.createElement('input');
                checkbox.type = 'checkbox';
                checkbox.id = `country_${country.replace(/\s+/g, '_')}`;
                checkbox.value = country;
                checkbox.onchange = () => this.updateSelectedCountries();
                
                const label = document.createElement('label');
                label.htmlFor = checkbox.id;
                label.textContent = country;
                label.style.cursor = 'pointer';
                
                option.appendChild(checkbox);
                option.appendChild(label);
                dropdown.appendChild(option);
            });
        },

        /**
         * Actualizar países seleccionados
         */
        updateSelectedCountries() {
            const checkboxes = document.querySelectorAll('#countryDropdown input[type="checkbox"]');
            const selected = Array.from(checkboxes).filter(cb => cb.checked).map(cb => cb.value);
            
            const container = document.getElementById('selectedCountries');
            if (!container) return;
            
            if (selected.length === 0) {
                container.innerHTML = '<span class="placeholder">Ningún país seleccionado (se mostrarán todos)</span>';
            } else {
                container.innerHTML = selected.map(country => 
                    `<span class="country-tag">${country}<span class="remove" onclick="SupplementsComponents.filters.removeCountry('${country}')">&times;</span></span>`
                ).join('');
            }
            
            // Disparar evento personalizado para notificar cambio
            window.dispatchEvent(new CustomEvent('countriesChanged', { 
                detail: { countries: selected } 
            }));
        },

        /**
         * Remover país seleccionado
         * @param {string} country - País a remover
         */
        removeCountry(country) {
            const checkbox = document.getElementById(`country_${country.replace(/\s+/g, '_')}`);
            if (checkbox) {
                checkbox.checked = false;
                this.updateSelectedCountries();
            }
        },

        /**
         * Obtener filtros actuales
         * @returns {Object} Filtros aplicados
         */
        getCurrentFilters() {
            const ingredientSelect = document.getElementById('ingredientSelect');
            const typeSelect = document.getElementById('typeSelect');
            const countryCheckboxes = document.querySelectorAll('#countryDropdown input[type="checkbox"]:checked');
            
            return {
                ingredient: ingredientSelect?.value || 'all',
                ingredient_type: typeSelect?.value || 'all',
                countries: Array.from(countryCheckboxes).map(cb => cb.value)
            };
        },

        /**
         * Limpiar todos los filtros
         */
        clear() {
            // Limpiar selectores
            const selects = ['ingredientSelect', 'typeSelect'];
            selects.forEach(id => {
                const select = document.getElementById(id);
                if (select) select.value = 'all';
            });
            
            // Limpiar países
            const checkboxes = document.querySelectorAll('#countryDropdown input[type="checkbox"]');
            checkboxes.forEach(cb => cb.checked = false);
            this.updateSelectedCountries();
        }
    },

    /**
     * Componente de comparación regulatoria
     */
    regulatoryComparison: {
        /**
         * Renderizar tabla de comparación
         * @param {Object} data - Datos de comparación
         * @param {Array} countries - Países a comparar
         */
        renderTable(data, countries) {
            const container = document.getElementById('comparisonResults');
            if (!container) return;

            if (!countries || countries.length === 0) {
                container.innerHTML = '<div class="info-message">No se encontró información para los países seleccionados.</div>';
                return;
            }

            // Crear tabla
            const table = document.createElement('table');
            table.className = 'comparison-table';

            // Header
            const thead = document.createElement('thead');
            const headerRow = document.createElement('tr');
            
            // Primera columna: Categoría
            const categoryHeader = document.createElement('th');
            categoryHeader.textContent = 'Aspecto Regulatorio';
            categoryHeader.style.minWidth = '200px';
            headerRow.appendChild(categoryHeader);
            
            // Columnas de países
            countries.forEach(country => {
                const countryHeader = document.createElement('th');
                countryHeader.className = 'country-header-cell';
                const countryCode = data[country]?.country_code || 'XX';
                countryHeader.innerHTML = `
                    <span class="country-flag">${this.getCountryFlag(countryCode)}</span>
                    <div>${country}</div>
                `;
                headerRow.appendChild(countryHeader);
            });
            
            thead.appendChild(headerRow);
            table.appendChild(thead);

            // Body
            const tbody = document.createElement('tbody');
            
            // Categorías a comparar
            const categories = [
                { key: 'instrumento_legal', label: 'Instrumento Legal' },
                { key: 'definicion_legal', label: 'Definición Legal' },
                { key: 'categoria_regulatoria', label: 'Categoría Regulatoria' },
                { key: 'proceso_registro', label: 'Proceso de Registro' },
                { key: 'tiempo_aprobacion', label: 'Tiempo de Aprobación' },
                { key: 'propiedades_salud', label: 'Declaraciones de Salud' }
            ];

            categories.forEach(category => {
                const row = document.createElement('tr');
                
                // Celda de categoría
                const categoryCell = document.createElement('td');
                categoryCell.className = 'category-cell';
                categoryCell.textContent = category.label;
                row.appendChild(categoryCell);
                
                // Celdas de países
                countries.forEach(country => {
                    const countryCell = document.createElement('td');
                    const section = data[country]?.sections?.[category.key];
                    
                    if (section) {
                        countryCell.innerHTML = this.renderSectionContent(section);
                    } else {
                        countryCell.innerHTML = '<em style="color: #999;">No disponible</em>';
                    }
                    
                    row.appendChild(countryCell);
                });
                
                tbody.appendChild(row);
            });

            table.appendChild(tbody);
            container.innerHTML = '';
            container.appendChild(table);
        },

        /**
         * Renderizar contenido de una sección
         * @param {Object} section - Datos de la sección
         * @returns {string} HTML renderizado
         */
        renderSectionContent(section) {
            let content = section.content || 'No disponible';
            
            switch (section.type) {
                case 'timeline':
                    if (section.legal_time && section.industry_time) {
                        content = `
                            <div class="timeline-info">
                                <div class="timeline-item"><strong>Legal:</strong> ${section.legal_time}</div>
                                <div class="timeline-item"><strong>Industria:</strong> ${section.industry_time}</div>
                            </div>
                        `;
                    }
                    break;
                    
                case 'category':
                case 'registration_type':
                    content = `<span class="category-badge category-${section.value?.toLowerCase().replace(/\s+/g, '-')}">${section.value || content}</span>`;
                    break;
                    
                case 'health_claims':
                    const permitted = section.permitted;
                    content = `
                        <span class="status-badge ${permitted ? 'permitted' : 'not-permitted'}">
                            ${permitted ? '✅ Permitidas' : '❌ No permitidas'}
                        </span>
                    `;
                    break;
                    
                default:
                    // Procesar markdown básico
                    content = content
                        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                        .replace(/\*(.*?)\*/g, '<em>$1</em>')
                        .replace(/\n/g, '<br>');
            }
            
            return content;
        },

        /**
         * Obtener emoji de bandera por código de país
         * @param {string} countryCode - Código de país
         * @returns {string} Emoji de bandera
         */
        getCountryFlag(countryCode) {
            const flags = {
                'AR': '🇦🇷', 'BR': '🇧🇷', 'CL': '🇨🇱', 'CO': '🇨🇴', 
                'CR': '🇨🇷', 'MX': '🇲🇽', 'PE': '🇵🇪', 'UY': '🇺🇾'
            };
            return flags[countryCode] || '🏴';
        }
    },

    /**
     * Componente de gráficos
     */
    charts: {
        /**
         * Renderizar gráfico con Plotly
         * @param {string} containerId - ID del contenedor
         * @param {Object} chartData - Datos del gráfico
         * @param {string} fallbackMessage - Mensaje si no hay datos
         */
        render(containerId, chartData, fallbackMessage = 'Sin datos para el gráfico') {
            const container = document.getElementById(containerId);
            if (!container) return;

            if (chartData && chartData.data && chartData.layout) {
                Plotly.newPlot(containerId, chartData.data, chartData.layout, {responsive: true});
            } else {
                container.innerHTML = `
                    <div style="text-align:center; color:var(--text-secondary); padding:2rem;">
                        <i class="fas fa-chart-bar" style="font-size: 3rem; margin-bottom: 1rem; opacity: 0.3;"></i>
                        <p>${fallbackMessage}</p>
                    </div>
                `;
            }
        },

        /**
         * Mostrar error en gráfico
         * @param {string} containerId - ID del contenedor
         * @param {string} message - Mensaje de error
         */
        showError(containerId, message = 'Error cargando gráfico') {
            const container = document.getElementById(containerId);
            if (!container) return;

            container.innerHTML = `
                <div style="text-align:center; color:var(--error-color); padding:2rem;">
                    <i class="fas fa-exclamation-triangle" style="font-size: 3rem; margin-bottom: 1rem;"></i>
                    <p>${message}</p>
                </div>
            `;
        }
    },

    /**
     * Utilidades generales
     */
    utils: {
        /**
         * Formatear números para display
         * @param {number} value - Valor a formatear
         * @param {Object} options - Opciones de formato
         * @returns {string} Número formateado
         */
        formatNumber(value, options = {}) {
            if (value === null || value === undefined) return '-';
            
            const { decimals = 2, locale = 'es-ES' } = options;
            
            if (typeof value === 'number') {
                return value.toLocaleString(locale, {
                    minimumFractionDigits: decimals,
                    maximumFractionDigits: decimals
                });
            }
            
            return value.toString();
        },

        /**
         * Formatear booleanos para display
         * @param {boolean} value - Valor booleano
         * @returns {string} Valor formateado
         */
        formatBoolean(value) {
            if (value === null || value === undefined) return '-';
            return value ? '✓' : '✗';
        },

        /**
         * Debounce para funciones
         * @param {Function} func - Función a hacer debounce
         * @param {number} delay - Delay en ms
         * @returns {Function} Función con debounce
         */
        debounce(func, delay = 300) {
            let timeoutId;
            return function (...args) {
                clearTimeout(timeoutId);
                timeoutId = setTimeout(() => func.apply(this, args), delay);
            };
        }
    }
};

// Exportar para uso global
window.SupplementsComponents = SupplementsComponents;