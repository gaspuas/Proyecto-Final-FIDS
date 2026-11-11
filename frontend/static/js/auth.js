/* Validacion local previa al envio de login y registro al servidor. */

const MENSAJES_CAMPO_VACIO = {
    nombre: 'Ingresá tu nombre.',
    email: 'Ingresá tu email.',
    password: 'Ingresá tu contraseña.',
};

function obtenerError(campo) {
    if (!campo.value.trim()) {
        return MENSAJES_CAMPO_VACIO[campo.name];
    }
    if (campo.validity.typeMismatch) {
        return 'Ingresá un email válido.';
    }
    if (campo.minLength > 0 && campo.value.length < campo.minLength) {
        return `La contraseña debe tener al menos ${campo.minLength} caracteres.`;
    }
    return null;
}

function mostrarError(campo, mensaje) {
    const elementoError = document.getElementById(`${campo.id}-error`);
    elementoError.textContent = mensaje || '';
    elementoError.hidden = !mensaje;

    if (mensaje) {
        campo.setAttribute('aria-invalid', 'true');
    } else {
        campo.removeAttribute('aria-invalid');
    }
}

function validarCampo(campo) {
    const mensaje = obtenerError(campo);
    mostrarError(campo, mensaje);
    return !mensaje;
}

document.querySelectorAll('.autenticacion form').forEach((formulario) => {
    const campos = Array.from(formulario.querySelectorAll('input'));
    // Con JavaScript activo, los errores se muestran debajo de cada campo
    formulario.noValidate = true;

    campos.forEach((campo) => {
        campo.addEventListener('input', () => {
            if (campo.hasAttribute('aria-invalid')) {
                validarCampo(campo);
            }
        });
    });

    formulario.addEventListener('submit', (evento) => {
        const invalidos = campos.filter((campo) => !validarCampo(campo));
        if (invalidos.length > 0) {
            evento.preventDefault();
            invalidos[0].focus();
        }
    });
});
