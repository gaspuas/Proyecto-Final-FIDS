from flask import Flask


def register_api_routes(app: Flask) -> None:
    from backend.src.routes.admin import admin_bp
    from backend.src.routes.auth import auth_bp
    from backend.src.routes.compras import compras_bp
    from backend.src.routes.funciones import funciones_bp
    from backend.src.routes.peliculas import peliculas_bp
    from backend.src.routes.servicios import servicios_bp

    for blueprint in (
        admin_bp,
        auth_bp,
        compras_bp,
        funciones_bp,
        peliculas_bp,
        servicios_bp,
    ):
        app.register_blueprint(blueprint)