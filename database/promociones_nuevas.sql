-- Opcional: ejecutar UNA vez para añadir estas dos promociones a tu MySQL local.
-- No modifica la estructura ni las películas existentes.
INSERT INTO novedades (titulo, descripcion, imagen_url, tipo, enlace, orden, fecha_inicio, fecha_fin, activo)
SELECT 'Combo pochoclos + bebida', 'Disfrutá tu película con pochoclos y una bebida bien fría.',
       '/static/img/novedades/promo_combo_pochoclos_bebida.webp', 'oferta', '/peliculas/', 3, NULL, NULL, 1
WHERE NOT EXISTS (SELECT 1 FROM novedades WHERE imagen_url = '/static/img/novedades/promo_combo_pochoclos_bebida.webp');

INSERT INTO novedades (titulo, descripcion, imagen_url, tipo, enlace, orden, fecha_inicio, fecha_fin, activo)
SELECT 'Cine en familia', 'Compartí la magia del cine con quienes más querés.',
       '/static/img/novedades/promo_cine_en_familia.webp', 'publicidad', '/peliculas/', 4, NULL, NULL, 1
WHERE NOT EXISTS (SELECT 1 FROM novedades WHERE imagen_url = '/static/img/novedades/promo_cine_en_familia.webp');
