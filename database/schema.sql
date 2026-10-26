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
-- Carga inicial de datos de prueba
-- -----------------------------------------------------
INSERT INTO locales_salas (nombre_local, numero_sala, capacidad_total, filas, columnas) VALUES
('Paradiso Central', 1, 50, 5, 10),
('Paradiso Central', 2, 50, 5, 10),
('Paradiso Norte', 1, 40, 4, 10);

INSERT INTO servicios (nombre, categoria, precio, descripcion) VALUES
('Combo Pochoclos + Bebida', 'comida', 4500.00, 'Pochoclos medianos y gaseosa de 500ml'),
('Estacionamiento (3 horas)', 'estacionamiento', 2000.00, 'Válido para el estacionamiento del complejo'),
('Acceso Sala VIP', 'servicio', 1500.00, 'Acceso al lounge exclusivo antes de la función');