'use client';

import { useEffect, useState } from 'react';
import EmpresaCard from './EmpresaCard';
import RightsStrip from './RightsStrip';
import { getEmpresas, type EmpresaCard as EmpresaCardData } from '../lib/api';

type Filters = { sin_titulo: boolean; jornada_corta: boolean; seguro: boolean; cerca: boolean };

export default function SearchClient() {
  const [q, setQ] = useState('');
  const [filters, setFilters] = useState<Filters>({ sin_titulo: false, jornada_corta: false, seguro: false, cerca: false });
  const [items, setItems] = useState<EmpresaCardData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [geo, setGeo] = useState<{ lat: number; lon: number } | null>(null);

  useEffect(() => {
    void load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filters.sin_titulo, filters.jornada_corta, filters.seguro, filters.cerca, geo]);

  async function load() {
    try {
      setLoading(true);
      setError('');
      const result = await getEmpresas({
        q,
        sin_titulo: filters.sin_titulo,
        jornada_corta: filters.jornada_corta,
        seguro: filters.seguro,
        lat: filters.cerca && geo ? geo.lat : undefined,
        lon: filters.cerca && geo ? geo.lon : undefined,
      });
      setItems(result);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'No se pudo cargar la información.');
    } finally {
      setLoading(false);
    }
  }

  function toggle(key: keyof Filters) {
    if (key === 'cerca' && !filters.cerca) {
      if (!navigator.geolocation) {
        setError('Tu navegador no permite usar ubicación. Prueba con ciudad o el buscador.');
        return;
      }
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setGeo({ lat: position.coords.latitude, lon: position.coords.longitude });
          setFilters((f) => ({ ...f, cerca: true }));
        },
        () => setError('No se pudo acceder a tu ubicación. Puedes seguir usando los otros filtros.'),
        { enableHighAccuracy: false, timeout: 7000, maximumAge: 300000 },
      );
      return;
    }
    setFilters((f) => ({ ...f, [key]: !f[key] }));
  }

  return (
    <>
      <section className="hero hero-aero">
        <h1>Busca empleo con más tranquilidad.</h1>
        <p>Revisa qué dicen otras personas, mira sanciones y encuentra puestos más fáciles de postular.</p>
        <div className="search-row">
          <input
            className="search-input"
            value={q}
            onChange={(e) => setQ(e.target.value)}
            onKeyDown={(e) => { if (e.key === 'Enter') void load(); }}
            placeholder="Empresa, rubro o ciudad..."
            aria-label="Buscar empresa, rubro o ciudad"
          />
          <button className="primary-btn" onClick={() => void load()}>Buscar</button>
        </div>
        <div className="filters" aria-label="Filtros rápidos">
          <button className={`filter-btn ${filters.sin_titulo ? 'active' : ''}`} onClick={() => toggle('sin_titulo')}>Sin título</button>
          <button className={`filter-btn ${filters.jornada_corta ? 'active' : ''}`} onClick={() => toggle('jornada_corta')}>Jornada corta</button>
          <button className={`filter-btn ${filters.cerca ? 'active' : ''}`} onClick={() => toggle('cerca')}>Cerca de mí</button>
          <button className={`filter-btn ${filters.seguro ? 'active' : ''}`} onClick={() => toggle('seguro')}>Seguro</button>
        </div>
      </section>

      <div className="section-head">
        <div>
          <h2>Empresas destacadas</h2>
          <p>Ordenadas por puntaje, de mayor a menor.</p>
        </div>
        <span className="muted">{items.length} resultados</span>
      </div>

      {error && <div className="error" role="alert">{error}</div>}
      {loading ? <div className="loading">Cargando empresas...</div> : null}
      {!loading && items.length === 0 ? <div className="empty">No encontramos empresas con esos filtros. Prueba quitando uno.</div> : null}
      {!loading && items.length > 0 ? <div className="grid">{items.map((empresa) => <EmpresaCard key={empresa.id} empresa={empresa} />)}</div> : null}

      <RightsStrip />
    </>
  );
}
