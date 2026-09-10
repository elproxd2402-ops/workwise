-- Migración 003: marca explícita de empresas de demostración.
-- No borra ninguna tabla ni dato existente.

ALTER TABLE empresas
    ADD COLUMN IF NOT EXISTS es_demo BOOLEAN NOT NULL DEFAULT FALSE;

-- Marca como demo las empresas de ejemplo que ya existían (por nombre).
-- Si en el futuro agregas más empresas de demo, márcalas también así o
-- pon es_demo = TRUE directamente al insertarlas.
UPDATE empresas
SET es_demo = TRUE
WHERE nombre ILIKE '%demo%';
