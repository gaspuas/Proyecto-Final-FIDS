-- TokenSession: migración incremental, sin borrar datos ni recrear tablas.
-- El hash SHA-256 del token se guarda en MySQL; el token sin hash sólo sale en login.
-- Todos los valores de expira_en y revocado_en se interpretan como UTC.
CREATE TABLE IF NOT EXISTS sesiones (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    token_hash CHAR(64) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
    creado_en DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    expira_en DATETIME(6) NOT NULL,
    revocado_en DATETIME(6) NULL,
    CONSTRAINT uq_sesiones_token_hash UNIQUE (token_hash),
    INDEX idx_sesiones_usuario (usuario_id),
    INDEX idx_sesiones_expira (expira_en),
    CONSTRAINT fk_sesiones_usuario FOREIGN KEY (usuario_id)
        REFERENCES usuarios(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
