/* Validación visual de login y registro. El backend vuelve a validar todo. */
const MENSAJES_CAMPO_VACIO = {
    nombre: 'Ingresá tu nombre.',
    email: 'Ingresá tu email.',
    password: 'Ingresá tu contraseña.',
    password_confirmacion: 'Repetí tu contraseña.',
    fecha_nacimiento: 'Ingresá tu fecha de nacimiento.',
    acepta_terminos: 'Para registrarte, tenés que aceptar los términos y condiciones.'
};

function mostrarError(campo, mensaje) {
    const error = document.getElementById(`${campo.id}-error`);
    if (!error) return;
    error.textContent = mensaje || '';
    error.hidden = !mensaje;
    if (mensaje) campo.setAttribute('aria-invalid', 'true');
    else campo.removeAttribute('aria-invalid');
}

function obtenerError(campo, formulario) {
    if (campo.type === 'checkbox') {
        return campo.required && !campo.checked ? MENSAJES_CAMPO_VACIO[campo.name] : null;
    }
    if (!campo.value.trim()) return MENSAJES_CAMPO_VACIO[campo.name] || 'Completá este campo.';
    if (campo.name === 'email' && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(campo.value.trim())) {
        return 'Ingresá un email válido (por ejemplo, nombre@dominio.com).';
    }
    if (campo.minLength > 0 && campo.value.length < campo.minLength) {
        return `La contraseña debe tener al menos ${campo.minLength} caracteres.`;
    }
    if (campo.name === 'password_confirmacion') {
        const clave = formulario.querySelector('[name="password"]');
        if (clave && campo.value !== clave.value) return 'Las contraseñas no coinciden.';
    }
    if (campo.name === 'fecha_nacimiento') {
        const fecha = new Date(`${campo.value}T12:00:00`);
        const hoy = new Date();
        if (Number.isNaN(fecha.getTime()) || fecha > hoy) return 'Ingresá una fecha de nacimiento válida, no futura.';
    }
    return null;
}

document.querySelectorAll('.autenticacion form').forEach((formulario) => {
    const campos = Array.from(formulario.querySelectorAll('input:not([type="hidden"])'));
    formulario.noValidate = true;
    const fechaNacimiento = formulario.querySelector('[name="fecha_nacimiento"]');
    if (fechaNacimiento) {
        const hoy = new Date();
        const fechaLocal = new Date(hoy.getTime() - hoy.getTimezoneOffset() * 60000);
        fechaNacimiento.max = fechaLocal.toISOString().slice(0, 10);
    }
    campos.forEach((campo) => {
        const evento = campo.type === 'checkbox' || campo.type === 'date' ? 'change' : 'input';
        campo.addEventListener(evento, () => {
            if (campo.hasAttribute('aria-invalid')) mostrarError(campo, obtenerError(campo, formulario));
            if (campo.name === 'password') {
                const confirmacion = formulario.querySelector('[name="password_confirmacion"]');
                if (confirmacion && confirmacion.value) mostrarError(confirmacion, obtenerError(confirmacion, formulario));
            }
        });
    });
    formulario.addEventListener('submit', (evento) => {
        const invalidos = campos.filter((campo) => {
            const error = obtenerError(campo, formulario);
            mostrarError(campo, error);
            return Boolean(error);
        });
        if (invalidos.length) {
            evento.preventDefault();
            invalidos[0].focus();
        }
    });
});
