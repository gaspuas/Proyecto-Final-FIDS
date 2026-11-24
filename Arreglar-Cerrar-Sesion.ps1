# Corrige exclusivamente el estilo del boton "Cerrar sesion".
# Conserva intactos el carrusel y el resto de la hoja de estilos.
$ErrorActionPreference = 'Stop'
$archivo = Join-Path $PSScriptRoot 'frontend\static\css\estilos.css'
if (-not (Test-Path -LiteralPath $archivo)) {
    throw "No encuentro $archivo. Guarda este script en la raiz de Proyecto-Final-FIDS."
}
$marca = '/* FIX CERRAR SESION - INICIO */'
$css = [System.IO.File]::ReadAllText($archivo)
if ($css.Contains($marca)) {
    Write-Host 'El arreglo ya esta aplicado. No se modifico nada.'
    exit 0
}
$parche = @'

/* FIX CERRAR SESION - INICIO */
/* Igualar el boton del formulario de salida a los enlaces de la barra */
.nav__menu form {
    margin: 0;
    padding: 0;
    display: flex;
    align-items: center;
}
.nav__menu form button.navbar__link {
    appearance: none;
    -webkit-appearance: none;
    background: transparent;
    border: 0;
    color: var(--color-texto-secundario);
    font-family: inherit;
    font-size: 0.95rem;
    font-weight: 500;
    line-height: inherit;
    text-decoration: none;
    padding: 0.4rem 0.8rem;
    border-radius: 4px;
    cursor: pointer;
    transition: all 0.2s ease;
}
.nav__menu form button.navbar__link:hover,
.nav__menu form button.navbar__link:focus-visible {
    color: var(--color-dorado);
    background-color: rgba(212, 175, 55, 0.15);
}
/* FIX CERRAR SESION - FIN */
'@
Copy-Item -LiteralPath $archivo -Destination "$archivo.bak-cerrar-sesion" -Force
[System.IO.File]::AppendAllText($archivo, $parche, [System.Text.UTF8Encoding]::new($false))
Write-Host 'Listo: corregido Cerrar sesion. El carrusel y los demas estilos no se tocaron.'
Write-Host 'Se guardo una copia de seguridad: estilos.css.bak-cerrar-sesion'

