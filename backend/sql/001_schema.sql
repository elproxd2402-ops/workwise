CREATE TABLE IF NOT EXISTS empresas (
    id BIGSERIAL PRIMARY KEY,
    nombre VARCHAR(180) NOT NULL,
    sector VARCHAR(120),
    ciudad VARCHAR(120),
    exige_titulo BOOLEAN NOT NULL DEFAULT FALSE,
    apto_joven BOOLEAN NOT NULL DEFAULT TRUE,
    resumen_ia TEXT,
    puntaje DOUBLE PRECISION NOT NULL DEFAULT 0 CHECK (puntaje >= 0 AND puntaje <= 100),
    semaforo VARCHAR(10) NOT NULL DEFAULT 'rojo' CHECK (semaforo IN ('verde', 'amarillo', 'rojo')),
    actualizado_ia TIMESTAMPTZ,
    latitud DOUBLE PRECISION,
    longitud DOUBLE PRECISION,
    web_aplicacion VARCHAR(500),
    es_demo BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS resenas (
    id BIGSERIAL PRIMARY KEY,
    empresa_id BIGINT NOT NULL REFERENCES empresas(id) ON DELETE CASCADE,
    texto TEXT NOT NULL,
    rating INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
    fecha DATE,
    fuente VARCHAR(80),
    url_fuente VARCHAR(500)
);

CREATE TABLE IF NOT EXISTS sanciones_sunafil (
    id BIGSERIAL PRIMARY KEY,
    empresa_id BIGINT NOT NULL REFERENCES empresas(id) ON DELETE CASCADE,
    tipo VARCHAR(200) NOT NULL,
    fecha DATE,
    fuente VARCHAR(120),
    url_fuente VARCHAR(500)
);

CREATE TABLE IF NOT EXISTS ofertas (
    id BIGSERIAL PRIMARY KEY,
    empresa_id BIGINT NOT NULL REFERENCES empresas(id) ON DELETE CASCADE,
    titulo_puesto VARCHAR(180) NOT NULL,
    descripcion TEXT,
    requiere_titulo BOOLEAN NOT NULL DEFAULT FALSE,
    jornada_horas DOUBLE PRECISION,
    apto_joven BOOLEAN NOT NULL DEFAULT TRUE,
    alertas TEXT,
    url_aplicacion VARCHAR(500)
);

CREATE INDEX IF NOT EXISTS idx_empresas_nombre ON empresas(nombre);
CREATE INDEX IF NOT EXISTS idx_empresas_ciudad ON empresas(ciudad);
CREATE INDEX IF NOT EXISTS idx_empresas_puntaje ON empresas(puntaje DESC);
CREATE INDEX IF NOT EXISTS idx_resenas_empresa ON resenas(empresa_id);
CREATE INDEX IF NOT EXISTS idx_sanciones_empresa ON sanciones_sunafil(empresa_id);
CREATE INDEX IF NOT EXISTS idx_ofertas_empresa ON ofertas(empresa_id);
