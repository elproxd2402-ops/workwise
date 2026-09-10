import Link from 'next/link';
import type { EmpresaCard as EmpresaCardData } from '../lib/api';

export default function EmpresaCard({ empresa }: { empresa: EmpresaCardData }) {
  return (
    <article className="card">
      <div className="score-row">
        <div>
          <span className="muted">Puntaje</span>
          <div className="score">{empresa.puntaje}</div>
        </div>
        <span className={`traffic ${empresa.semaforo}`} aria-label={`Semáforo ${empresa.semaforo}`} />
      </div>
      <h3>{empresa.nombre} {empresa.es_demo && <span className="badge demo-badge" title="Datos ficticios de demostración">DEMO</span>}</h3>
      <div className="meta">{empresa.sector ?? 'Sector no indicado'} · {empresa.ciudad ?? 'Ciudad no indicada'}</div>
      <p className="summary">{empresa.resumen_ia}</p>
      <div className="badges">
        {!empresa.exige_titulo && <span className="badge good">Sin título</span>}
        {empresa.ofertas_cortas > 0 && <span className="badge good">Jornada corta</span>}
        {empresa.sanciones === 0 ? <span className="badge good">Sin sanciones registradas</span> : <span className="badge warn">{empresa.sanciones} sanción(es)</span>}
        {empresa.distancia_km !== null && <span className="badge">A {empresa.distancia_km} km</span>}
      </div>
      <div className="card-footer">
        <span className="muted">{empresa.apto_joven ? 'Apto para joven' : 'No apto a los 17'}</span>
        <Link className="primary-btn" href={`/empresas/${empresa.id}`}>Ver detalles</Link>
      </div>
    </article>
  );
}
