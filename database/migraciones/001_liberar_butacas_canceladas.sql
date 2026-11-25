-- Migración: liberar las butacas de las compras canceladas.
--
--
-- Uso (desde la raíz del repo):
--   docker exec -i cine_paradiso_db mysql -ucineAdmin -p cine_paradiso_db < database/migraciones/001_liberar_butacas_canceladas.sql

-- Las entradas de compras ya canceladas dejan de ocupar la butaca.
UPDATE entradas_detalle AS ed
INNER JOIN compras AS c ON c.id = ed.compra_id
SET ed.activa = NULL
WHERE c.estado_qr = 'cancelado';
