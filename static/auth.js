// ==============================================
// AUTENTICACIÓN PORTAL ILAR
// ==============================================
// La configuración se carga desde config.js - NO declarar variables aquí

// Esperar a que la configuración esté disponible
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
    
    initializeAuth();
});

// Inicializar autenticación
function initializeAuth() {
    try {
        // Crear cliente de Supabase usando la configuración global
        window.supabaseClient = window.supabase.createClient(
            window.ILAR_CONFIG.SUPABASE_URL, 
            window.ILAR_CONFIG.SUPABASE_ANON_KEY
        );
        
        console.log('✅ Cliente de Supabase inicializado');
        
        initializeTabs();
        initializePasswordStrength();
        checkExistingSession();
        setupFormHandlers();
        
    } catch (error) {
        console.error('❌ Error inicializando autenticación:', error);
        showNotification('Error de inicialización. Recarga la página.', 'error');
    }
}

function initializeTabs() {
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const targetTab = button.getAttribute('data-tab');
            
            // Remover clases activas
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));
            
            // Agregar clases activas
            button.classList.add('active');
            const targetContent = document.getElementById(targetTab);
            if (targetContent) {
                targetContent.classList.add('active');
            }
        });
    });
}

function setupFormHandlers() {
    // Formulario de Login
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }
    
    // Formulario de Registro
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', handleRegister);
    }
}

async function checkExistingSession() {
    try {
        const { data: { session } } = await window.supabaseClient.auth.getSession();
        if (session) {
            console.log('Usuario ya logueado, redirigiendo...');
            window.location.href = 'dashboard.html';
        }
    } catch (error) {
        console.error('Error checking session:', error);
    }
}

async function handleLogin(e) {
    e.preventDefault();
    
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;
    const rememberMe = document.getElementById('rememberMe').checked;
    
    if (!email || !password) {
        showNotification('Por favor completa todos los campos', 'error');
        return;
    }
    
    try {
        showLoading(true);
        
        const { data, error } = await window.supabaseClient.auth.signInWithPassword({
            email: email,
            password: password
        });
        
        if (error) {
            throw error;
        }
        
        // Login exitoso
        if (rememberMe) {
            localStorage.setItem('rememberUser', email);
        }
        
        showNotification('Login exitoso! Redirigiendo...', 'success');
        
        // Redirigir después de un breve delay
        setTimeout(() => {
            window.location.href = 'dashboard.html';
        }, 1500);
        
    } catch (error) {
        console.error('Error during login:', error);
        
        let errorMessage = 'Error al iniciar sesión';
        if (error.message.includes('Invalid login credentials')) {
            errorMessage = 'Email o contraseña incorrectos';
        } else if (error.message.includes('Email not confirmed')) {
            errorMessage = 'Por favor confirma tu email antes de iniciar sesión';
        }
        
        showNotification(errorMessage, 'error');
    } finally {
        showLoading(false);
    }
}

async function handleRegister(e) {
    e.preventDefault();
    
    const firstName = document.getElementById('firstName').value;
    const lastName = document.getElementById('lastName').value;
    const email = document.getElementById('registerEmail').value;
    const organization = document.getElementById('organization').value;
    const password = document.getElementById('registerPassword').value;
    const confirmPassword = document.getElementById('confirmPassword').value;
    const acceptTerms = document.getElementById('acceptTerms').checked;
    
    // Validaciones
    if (!firstName || !lastName || !email || !password || !confirmPassword) {
        showNotification('Por favor completa todos los campos obligatorios', 'error');
        return;
    }
    
    if (password !== confirmPassword) {
        showNotification('Las contraseñas no coinciden', 'error');
        return;
    }
    
    if (password.length < 6) {
        showNotification('La contraseña debe tener al menos 6 caracteres', 'error');
        return;
    }
    
    if (!acceptTerms) {
        showNotification('Debes aceptar los términos y condiciones', 'error');
        return;
    }
    
    try {
        showLoading(true);
        
        const { data, error } = await window.supabaseClient.auth.signUp({
            email: email,
            password: password,
            options: {
                data: {
                    first_name: firstName,
                    last_name: lastName,
                    organization: organization,
                    full_name: `${firstName} ${lastName}`
                }
            }
        });
        
        if (error) {
            throw error;
        }
        
        showNotification('Cuenta creada exitosamente! Revisa tu email para confirmar.', 'success');
        
        // Cambiar a la pestaña de login
        setTimeout(() => {
            document.querySelector('[data-tab="login"]').click();
            document.getElementById('loginEmail').value = email;
        }, 2000);
        
    } catch (error) {
        console.error('Error during registration:', error);
        
        let errorMessage = 'Error al crear la cuenta';
        if (error.message.includes('User already registered')) {
            errorMessage = 'Ya existe una cuenta con este email';
        } else if (error.message.includes('Password should be at least')) {
            errorMessage = 'La contraseña debe tener al menos 6 caracteres';
        }
        
        showNotification(errorMessage, 'error');
    } finally {
        showLoading(false);
    }
}

// ==============================================
// RECUPERACIÓN DE CONTRASEÑA
// ==============================================
function showForgotPassword() {
    document.getElementById('forgotPasswordModal').style.display = 'block';
}

function closeForgotPassword() {
    document.getElementById('forgotPasswordModal').style.display = 'none';
}

async function sendPasswordReset() {
    const email = document.getElementById('forgotEmail').value;
    
    if (!email) {
        showNotification('Por favor ingresa tu email', 'error');
        return;
    }
    
    try {
        const { error } = await window.supabaseClient.auth.resetPasswordForEmail(email, {
            redirectTo: `${window.location.origin}/reset-password.html`
        });
        
        if (error) {
            throw error;
        }
        
        showNotification('Se ha enviado un enlace de recuperación a tu email', 'success');
        closeForgotPassword();
        
    } catch (error) {
        console.error('Error sending password reset:', error);
        showNotification('Error al enviar el enlace de recuperación', 'error');
    }
}

// Cerrar modal al hacer clic fuera
window.addEventListener('click', function(event) {
    const modal = document.getElementById('forgotPasswordModal');
    if (event.target === modal) {
        closeForgotPassword();
    }
});

// ==============================================
// UTILIDADES
// ==============================================
function togglePassword(inputId) {
    const input = document.getElementById(inputId);
    const button = input.nextElementSibling;
    const icon = button.querySelector('i');
    
    if (input.type === 'password') {
        input.type = 'text';
        icon.className = 'fas fa-eye-slash';
    } else {
        input.type = 'password';
        icon.className = 'fas fa-eye';
    }
}

function initializePasswordStrength() {
    const passwordInput = document.getElementById('registerPassword');
    const strengthFill = document.getElementById('strengthFill');
    const strengthText = document.getElementById('strengthText');
    
    if (passwordInput && strengthFill && strengthText) {
        passwordInput.addEventListener('input', function() {
            const password = this.value;
            const strength = calculatePasswordStrength(password);
            updatePasswordStrengthUI(strength, strengthFill, strengthText);
        });
    }
}

function calculatePasswordStrength(password) {
    let score = 0;
    
    if (password.length >= 6) score += 1;
    if (password.length >= 10) score += 1;
    if (/[a-z]/.test(password)) score += 1;
    if (/[A-Z]/.test(password)) score += 1;
    if (/[0-9]/.test(password)) score += 1;
    if (/[^A-Za-z0-9]/.test(password)) score += 1;
    
    return {
        score: score,
        level: score < 2 ? 'weak' : score < 4 ? 'medium' : 'strong'
    };
}

function updatePasswordStrengthUI(strength, fillElement, textElement) {
    const percentage = (strength.score / 6) * 100;
    fillElement.style.width = `${percentage}%`;
    
    switch (strength.level) {
        case 'weak':
            fillElement.style.background = '#F44336';
            textElement.textContent = 'Contraseña débil';
            textElement.style.color = '#F44336';
            break;
        case 'medium':
            fillElement.style.background = '#FF9800';
            textElement.textContent = 'Contraseña media';
            textElement.style.color = '#FF9800';
            break;
        case 'strong':
            fillElement.style.background = '#4CAF50';
            textElement.textContent = 'Contraseña fuerte';
            textElement.style.color = '#4CAF50';
            break;
    }
}

function showNotification(message, type = 'info') {
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
    
    // Ocultar después de 4 segundos
    setTimeout(() => {
        notification.classList.remove('show');
    }, 4000);
}

function showLoading(show) {
    let overlay = document.getElementById('loadingOverlay');
    if (!overlay) {
        overlay = document.createElement('div');
        overlay.id = 'loadingOverlay';
        overlay.className = 'loading-overlay';
        overlay.innerHTML = `
            <div class="loading-content">
                <div class="loading-spinner"></div>
                <p>Procesando...</p>
            </div>
        `;
        document.body.appendChild(overlay);
    }
    
    overlay.style.display = show ? 'flex' : 'none';
}

// Cargar email recordado al cargar la página
window.addEventListener('load', function() {
    const rememberedEmail = localStorage.getItem('rememberUser');
    if (rememberedEmail) {
        const emailInput = document.getElementById('loginEmail');
        const rememberCheckbox = document.getElementById('rememberMe');
        if (emailInput) emailInput.value = rememberedEmail;
        if (rememberCheckbox) rememberCheckbox.checked = true;
    }
});