-- Ejecutar una sola vez en cada base de datos existente (tambien admite repeticion).
-- Conserva los usuarios y las contraseñas anteriores.
USE cine_paradiso_db;

SET @existe = (SELECT COUNT(*) FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'usuarios' AND COLUMN_NAME = 'fecha_nacimiento');
SET @sql = IF(@existe = 0, 'ALTER TABLE usuarios ADD COLUMN fecha_nacimiento DATE NULL', 'SELECT ''Columna fecha_nacimiento ya existe'' AS resultado');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @existe = (SELECT COUNT(*) FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'usuarios' AND COLUMN_NAME = 'acepta_terminos');
SET @sql = IF(@existe = 0, 'ALTER TABLE usuarios ADD COLUMN acepta_terminos BOOLEAN NOT NULL DEFAULT FALSE', 'SELECT ''Columna acepta_terminos ya existe'' AS resultado');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @existe = (SELECT COUNT(*) FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'usuarios' AND COLUMN_NAME = 'fecha_aceptacion_terminos');
SET @sql = IF(@existe = 0, 'ALTER TABLE usuarios ADD COLUMN fecha_aceptacion_terminos DATETIME NULL', 'SELECT ''Columna fecha_aceptacion_terminos ya existe'' AS resultado');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @existe = (SELECT COUNT(*) FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'usuarios' AND COLUMN_NAME = 'recibir_promociones');
SET @sql = IF(@existe = 0, 'ALTER TABLE usuarios ADD COLUMN recibir_promociones BOOLEAN NOT NULL DEFAULT FALSE', 'SELECT ''Columna recibir_promociones ya existe'' AS resultado');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;
