-- Migración: liberar las butacas de las compras canceladas.
--
-- Para bases de datos ya creadas con el esquema anterior, donde
-- UNIQUE (funcion_id, numero_butaca) impedía volver a vender una butaca
-- cuya compra había sido cancelada (error 400 al comprar).
--
-- Uso (desde la raíz del repo):
--   docker exec -i cine_paradiso_db mysql -ucineAdmin -p cine_paradiso_db < database/migraciones/001_liberar_butacas_canceladas.sql

ALTER TABLE entradas_detalle
  ADD COLUMN activa TINYINT(1) NULL DEFAULT 1,
  DROP INDEX uq_funcion_butaca,
  ADD CONSTRAINT uq_funcion_butaca_activa UNIQUE (funcion_id, numero_butaca, activa);

-- Las entradas de compras ya canceladas dejan de ocupar la butaca.
UPDATE entradas_detalle AS ed
INNER JOIN compras AS c ON c.id = ed.compra_id
SET ed.activa = NULL
WHERE c.estado_qr = 'cancelado';
