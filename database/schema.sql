-- Script de Creación de la Base de Datos para Cine Paradiso
-- Sistema de Venta de Entradas - Hito 1

CREATE DATABASE IF NOT EXISTS cine_paradiso_db
  DEFAULT CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE cine_paradiso_db;

-- -----------------------------------------------------
-- 1. Tabla: usuarios
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS usuarios (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(100) NOT NULL,
  email VARCHAR(150) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  rol ENUM('cliente', 'administrador') NOT NULL DEFAULT 'cliente',
  fecha_registro DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- -----------------------------------------------------
-- 2. Tabla: locales_salas
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS locales_salas (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nombre_local VARCHAR(100) NOT NULL,
  numero_sala INT NOT NULL,
  capacidad_total INT NOT NULL,
  filas INT NOT NULL,
  columnas INT NOT NULL,
  CONSTRAINT uq_local_sala UNIQUE (nombre_local, numero_sala)
) ENGINE=InnoDB;

-- -----------------------------------------------------
-- 3. Tabla: peliculas
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS peliculas (
  id INT AUTO_INCREMENT PRIMARY KEY,
  api_id VARCHAR(50) NULL,
  titulo VARCHAR(150) NOT NULL,
  sinopsis TEXT NULL,
  poster_url VARCHAR(500) NULL,
  duracion_minutos INT NOT NULL,
  clasificacion VARCHAR(20) NULL,
  genero VARCHAR(100) NULL,
  director VARCHAR(100) NULL,
  es_reestreno BOOLEAN DEFAULT TRUE
) ENGINE=InnoDB;

-- -----------------------------------------------------
-- 4. Tabla: funciones
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS funciones (
  id INT AUTO_INCREMENT PRIMARY KEY,
  pelicula_id INT NOT NULL,
  sala_id INT NOT NULL,
  fecha_hora DATETIME NOT NULL,
  precio_base DECIMAL(10,2) NOT NULL,
  idioma VARCHAR(15) NOT NULL,
  formato VARCHAR(15) NOT NULL,
  CONSTRAINT fk_funciones_pelicula FOREIGN KEY (pelicula_id) REFERENCES peliculas(id) ON DELETE CASCADE,
  CONSTRAINT fk_funciones_sala FOREIGN KEY (sala_id) REFERENCES locales_salas(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- -----------------------------------------------------
-- 5. Tabla: compras
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS compras (
  id INT AUTO_INCREMENT PRIMARY KEY,
  usuario_id INT NOT NULL,
  fecha_compra DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  monto_total DECIMAL(10,2) NOT NULL,
  codigo_qr VARCHAR(255) NOT NULL UNIQUE,
  estado_qr ENUM('activo', 'usado', 'cancelado') NOT NULL DEFAULT 'activo',
  CONSTRAINT fk_compras_usuario FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- -----------------------------------------------------
-- 6. Tabla: entradas_detalle
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS entradas_detalle (
  id INT AUTO_INCREMENT PRIMARY KEY,
  compra_id INT NOT NULL,
  funcion_id INT NOT NULL,
  numero_butaca VARCHAR(10) NOT NULL,
  precio DECIMAL(10,2) NOT NULL,
  CONSTRAINT fk_entradas_compra FOREIGN KEY (compra_id) REFERENCES compras(id) ON DELETE CASCADE,
  CONSTRAINT fk_entradas_funcion FOREIGN KEY (funcion_id) REFERENCES funciones(id) ON DELETE CASCADE,
  CONSTRAINT uq_funcion_butaca UNIQUE (funcion_id, numero_butaca)
) ENGINE=InnoDB;

-- -----------------------------------------------------
-- 7. Tabla: servicios
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS servicios (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(100) NOT NULL,
  categoria ENUM('comida', 'bebida', 'estacionamiento', 'servicio') NOT NULL,
  precio DECIMAL(10,2) NOT NULL,
  descripcion TEXT NULL
) ENGINE=InnoDB;

-- -----------------------------------------------------
-- 8. Tabla: compras_servicios (Relación N:M)
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS compras_servicios (
  id INT AUTO_INCREMENT PRIMARY KEY,
  compra_id INT NOT NULL,
  servicio_id INT NOT NULL,
  cantidad INT NOT NULL DEFAULT 1,
  precio_unitario DECIMAL(10,2) NOT NULL,
  CONSTRAINT fk_cs_compra FOREIGN KEY (compra_id) REFERENCES compras(id) ON DELETE CASCADE,
  CONSTRAINT fk_cs_servicio FOREIGN KEY (servicio_id) REFERENCES servicios(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- -----------------------------------------------------
-- 9. Tabla: resenas (Punto Deseable: Calificación por Asistencia)
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS resenas (
  id INT AUTO_INCREMENT PRIMARY KEY,
  usuario_id INT NOT NULL,
  pelicula_id INT NOT NULL,
  compra_id INT NOT NULL,
  puntuacion INT CHECK (puntuacion BETWEEN 1 AND 5),
  comentario TEXT NULL,
  fecha DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_resenas_usuario FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
  CONSTRAINT fk_resenas_pelicula FOREIGN KEY (pelicula_id) REFERENCES peliculas(id) ON DELETE CASCADE,
  CONSTRAINT fk_resenas_compra FOREIGN KEY (compra_id) REFERENCES compras(id) ON DELETE CASCADE,
  CONSTRAINT uq_usuario_funcion_resena UNIQUE (usuario_id, compra_id)
) ENGINE=InnoDB;

-- -----------------------------------------------------
-- Carga inicial de datos de prueba
-- -----------------------------------------------------
INSERT IGNORE INTO locales_salas (nombre_local, numero_sala, capacidad_total, filas, columnas) VALUES
('Paradiso Central', 1, 50, 5, 10),
('Paradiso Central', 2, 50, 5, 10),
('Paradiso Norte', 1, 40, 4, 10);

INSERT IGNORE INTO servicios (nombre, categoria, precio, descripcion) VALUES
('Combo Pochoclos + Bebida', 'comida', 4500.00, 'Pochoclos medianos y gaseosa de 500ml'),
('Estacionamiento (3 horas)', 'estacionamiento', 2000.00, 'Válido para el estacionamiento del complejo'),
('Acceso Sala VIP', 'servicio', 1500.00, 'Acceso al lounge exclusivo antes de la función');

INSERT INTO peliculas (
    api_id, 
    titulo, 
    sinopsis, 
    poster_url, 
    duracion_minutos, 
    clasificacion, 
    genero, 
    director, 
    es_reestreno
) VALUES 
('tt0111161', 'The Shawshank Redemption', 'Dos hombres encarcelados entablan una fuerte amistad a lo largo de los años.', 'https://tmdb.org', 142, 'R', 'Drama', 'Frank Darabont', FALSE),
('tt0068646', 'The Godfather', 'El envejecido patriarca de una dinastía del crimen organizado transfiere el control a su reacio hijo.', 'https://tmdb.org', 175, 'R', 'Crimen, Drama', 'Francis Ford Coppola', FALSE),
('tt0468569', 'The Dark Knight', 'Cuando la amenaza conocida como el Joker causa estragos en Gotham, Batman debe aceptarla.', 'https://tmdb.org', 152, 'PG-13', 'Acción, Crimen', 'Christopher Nolan', TRUE),
('tt0137523', 'Fight Club', 'Un oficinista insomne y un desapegado fabricante de jabones forman un club de lucha subterráneo.', 'https://tmdb.org', 139, 'R', 'Drama', 'David Fincher', FALSE),
('tt0109830', 'Forrest Gump', 'Las presidencias de Kennedy y Johnson, los eventos de Vietnam y Watergate se desarrollan desde la perspectiva de un hombre de Alabama.', 'https://tmdb.org', 142, 'PG-13', 'Drama, Romance', 'Robert Zemeckis', TRUE),
('tt0133093', 'The Matrix', 'Un hacker descubre la verdadera naturaleza de su realidad y su rol en la guerra contra sus controladores.', 'https://tmdb.org', 136, 'R', 'Ciencia Ficción', 'Lana Wachowski', TRUE),
('tt0110912', 'Pulp Fiction', 'Las vidas de dos asesinos a sueldo, un boxeador, la esposa de un gángster y un par de bandidos se entrelazan.', 'https://tmdb.org', 154, 'R', 'Crimen, Drama', 'Quentin Tarantino', FALSE),
('tt0120737', 'The Lord of the Rings: The Fellowship of the Ring', 'Un manso hobbit de la Comarca y ocho compañeros se embarcan en un viaje para destruir el Anillo Único.', 'https://tmdb.org', 178, 'PG-13', 'Aventura, Fantasía', 'Peter Jackson', TRUE),
('tt0816692', 'Interstellar', 'Un equipo de exploradores viaja a través de un agujero de gusano en el espacio en un intento por asegurar la supervivencia de la humanidad.', 'https://tmdb.org', 169, 'PG-13', 'Ciencia Ficción, Drama', 'Christopher Nolan', FALSE),
('tt1375666', 'Inception', 'A un ladrón que roba secretos corporativos a través del uso de la tecnología de compartir sueños se le da la tarea inversa.', 'https://tmdb.org', 148, 'PG-13', 'Acción, Ciencia Ficción', 'Christopher Nolan', TRUE);

INSERT INTO funciones (
    pelicula_id, 
    sala_id, 
    fecha_hora, 
    precio_base, 
    idioma, 
    formato
) VALUES 
(1, 1, '2026-11-15 16:00:00', 4500.00, 'Subtitulada', '2D'),
(1, 2, '2026-11-15 19:30:00', 4500.00, 'Doblada', '2D'),
(2, 1, '2026-11-15 21:00:00', 4500.00, 'Subtitulada', '2D'),
(3, 3, '2026-11-16 14:00:00', 5800.00, 'Subtitulada', 'IMAX 3D'),
(3, 3, '2026-11-16 18:30:00', 5800.00, 'Doblada', 'IMAX 3D'),
(5, 2, '2026-11-16 15:00:00', 4500.00, 'Doblada', '2D'),
(6, 1, '2026-11-17 22:45:00', 5200.00, 'Subtitulada', '4XD'),
(8, 3, '2026-11-17 17:00:00', 5800.00, 'Subtitulada', 'IMAX 2D'),
(9, 2, '2026-11-18 20:00:00', 4500.00, 'Subtitulada', '2D'),
(10, 1, '2026-11-18 18:00:00', 5200.00, 'Doblada', '4XD');
