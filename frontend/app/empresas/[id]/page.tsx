'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import { getEmpresa, type EmpresaDetail } from '../../../lib/api';

export default function EmpresaPage({ params }: { params: Promise<{ id: string }> }) {
  const [empresa, setEmpresa] = useState<EmpresaDetail | null>(null);
  const [error, setError] = useState('');
  const [id, setId] = useState<number | null>(null);

  useEffect(() => {
    params.then(({ id: raw }) => setId(Number(raw)));
  }, [params]);

  useEffect(() => {
    if (!id) return;
    getEmpresa(id).then(setEmpresa).catch((e) => setError(e instanceof Error ? e.message : 'No se pudo cargar la empresa.'));
  }, [id]);

  if (error) return <main className="container"><div className="error">{error}</div></main>;
  if (!empresa) return <main className="container"><div className="loading">Cargando empresa...</div></main>;

  return (
    <main className="container">
      <div className="detail-hero">
        <Link href="/" className="back-link">← Volver a empresas</Link>
        <div className="card">
          <div className="meta">{empresa.sector ?? 'Sector no indicado'} · {empresa.ciudad ?? 'Ciudad no indicada'}</div>
          <h1>{empresa.nombre}</h1>
          {empresa.es_demo && (
            <div className="notice demo-notice">
              🧪 Esta es una empresa de <strong>demostración</strong>: sus datos son ficticios y solo sirven para probar la web.
            </div>
          )}
          <div className="score-shell">
            <span className={`traffic ${empresa.semaforo}`} aria-label={`Semáforo ${empresa.semaforo}`} />
            <div className="score-big">{empresa.puntaje}</div>
            <div className="score-copy">
              <strong>{empresa.semaforo === 'verde' ? 'Buena señal' : empresa.semaforo === 'amarillo' ? 'Ojo con esto' : 'Revisa bien antes de postular'}</strong>
              <span className="muted">puntaje de 100 · según datos y mejor puesto registrado</span>
            </div>
          </div>
          <p>{empresa.resumen_ia}</p>
          {empresa.actualizado_ia && <p className="muted">Resumen actualizado: {new Date(empresa.actualizado_ia).toLocaleDateString('es-PE')}</p>}
          <p className="muted" style={{ marginTop: 18, marginBottom: 4, fontWeight: 800 }}>¿Por qué tiene este puntaje?</p>
          <div className="breakdown">
            <div className="metric"><b>{empresa.reputacion}</b><span>Reputación / 40</span></div>
            <div className="metric"><b>{empresa.cumplimiento}</b><span>Cumplimiento / 30</span></div>
            <div className="metric"><b>{empresa.elegibilidad_juvenil}</b><span>Elegibilidad / 20</span></div>
            <div className="metric"><b>{empresa.facil_aplicar}</b><span>Fácil de aplicar / 10</span></div>
          </div>
        </div>
      </div>

      <section className="section-head"><div><h2>Puestos</h2><p>Mira las horas y alertas antes de aplicar.</p></div></section>
      <div className="card">
        {empresa.ofertas.length === 0 && <p className="muted">No hay ofertas registradas.</p>}
        {empresa.ofertas.map((oferta) => (
          <article className="offer" key={oferta.id}>
            <h3>{oferta.titulo_puesto}</h3>
            <p>{oferta.descripcion}</p>
            <div className="badges">
              {!oferta.requiere_titulo && <span className="badge good">Sin título</span>}
              {oferta.jornada_horas !== null && <span className="badge">{oferta.jornada_horas} h/día</span>}
              <span className={`badge ${oferta.apto_joven ? 'good' : 'warn'}`}>{oferta.apto_joven ? 'Apto para joven' : 'No apto a los 17'}</span>
            </div>
            {oferta.apto_joven ? (
              <p className="alert alert-good">✅ Este puesto cumple los criterios juveniles de esta web.</p>
            ) : (
              <p className="alert">⚠️ Ojo: este puesto no cumple los criterios que usamos para recomendar trabajos a jóvenes.</p>
            )}
            {oferta.alertas && <p className="alert">{oferta.alertas}</p>}
            {oferta.url_aplicacion && <a className="primary-btn apply-btn" href={oferta.url_aplicacion} target="_blank" rel="noreferrer">Aplicar</a>}
          </article>
        ))}
      </div>

      <section className="section-head"><div><h2>Reseñas</h2><p>Comentarios individuales importados desde fuentes registradas.</p></div></section>
      <div className="card">
        {empresa.resenas.length === 0 && <p className="muted">Todavía no hay reseñas.</p>}
        {empresa.resenas.map((review) => (
          <article className="review" key={review.id}>
            <div className="stars" aria-label={`${review.rating} de 5 estrellas`}>{'★'.repeat(review.rating)}{'☆'.repeat(5 - review.rating)}</div>
            <p>{review.texto}</p>
            <div className="meta">{review.fuente ?? 'Fuente no indicada'}{review.fecha ? ` · ${new Date(review.fecha).toLocaleDateString('es-PE')}` : ''}</div>
          </article>
        ))}
      </div>

      <section className="section-head"><div><h2>Sanciones SUNAFIL</h2><p>Registros asociados a esta empresa en la base de datos.</p></div></section>
      <div className="card">
        {empresa.sanciones_detalle.length === 0 ? <p className="muted">No hay sanciones registradas en nuestra base.</p> : empresa.sanciones_detalle.map((s) => (
          <article className="sanction" key={s.id}><strong>{s.tipo}</strong><div className="meta">{s.fecha ? new Date(s.fecha).toLocaleDateString('es-PE') : 'Fecha no indicada'}{s.fuente ? ` · ${s.fuente}` : ''}</div></article>
        ))}
      </div>

      <section className="info-strip">
        <h2>Tus derechos a los 17</h2>
        <p>La regla rápida: jornada máxima de 6 horas, nada de trabajo nocturno y derecho a denunciar ante SUNAFIL.</p>
        <Link className="primary-btn" href="/derechos">Leer la guía completa</Link>
      </section>
    </main>
  );
}
