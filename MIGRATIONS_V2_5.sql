-- MIGRATIONS V2.5 - OPTION B Implementation
-- Fecha: 2025-11-10 23:35:55

-- No se requieren migraciones SQL para esta versión
-- Las mejoras usan las columnas existentes:
-- - awaiting_continuation (ya existe)
-- - continuation_timestamp (ya existe)

-- Verificar que existan las columnas (por si acaso)
ALTER TABLE line_sessions
ADD COLUMN IF NOT EXISTS awaiting_continuation BOOLEAN DEFAULT FALSE;

ALTER TABLE line_sessions
ADD COLUMN IF NOT EXISTS continuation_timestamp TIMESTAMP;

-- Opcional: Agregar índice para mejorar performance de timeout check
CREATE INDEX IF NOT EXISTS idx_line_sessions_continuation
ON line_sessions(phone_number, awaiting_continuation, continuation_timestamp)
WHERE awaiting_continuation = TRUE;
