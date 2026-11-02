import base64
from io import BytesIO

import qrcode


def generar_qr_png(codigo_qr: str) -> bytes:
    """Genera la imagen PNG (en bytes) de un QR que contiene el código de la compra."""
    if not codigo_qr:
        raise ValueError("El código QR no puede estar vacío.")

    qr = qrcode.QRCode(
        version=None,  # tamaño automático según el contenido
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(codigo_qr)
    qr.make(fit=True)

    imagen = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    imagen.save(buffer, format="PNG")
    return buffer.getvalue()


def generar_qr_base64(codigo_qr: str) -> str:
    """
    Devuelve el QR como data URI, listo para usar en un <img src="..."> o en un JSON:
    "data:image/png;base64,iVBOR..."
    """
    png = generar_qr_png(codigo_qr)
    return "data:image/png;base64," + base64.b64encode(png).decode("ascii")
