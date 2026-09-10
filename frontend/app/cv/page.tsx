'use client';

import { useState } from 'react';
import Link from 'next/link';
import { asistenteCV, type CVResponse } from '../../lib/api';

const fields = [
  ['nombre', 'Nombre completo'],
  ['ciudad', 'Ciudad / región'],
  ['contacto', 'Correo o medio de contacto'],
  ['objetivo', '¿Qué trabajo buscas?'],
  ['educacion', 'Educación'],
  ['experiencia', 'Experiencia laboral (si tienes)'],
  ['proyectos', 'Proyectos, voluntariado o actividades'],
  ['habilidades', 'Habilidades'],
  ['cursos', 'Cursos o certificaciones'],
  ['idiomas', 'Idiomas'],
] as const;

export default function CVPage() {
  const [mode, setMode] = useState<'generar' | 'revisar'>('generar');
  const [data, setData] = useState<Record<string, string>>({});
  const [texto, setTexto] = useState('');
  const [result, setResult] = useState<CVResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  async function submit() {
    setLoading(true);
    setError('');
    try {
      const r = await asistenteCV(
        mode === 'generar'
          ? { accion: 'generar', datos: data }
          : { accion: 'revisar', texto_cv: texto },
      );
      setResult(r);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'No se pudo procesar el CV.');
    } finally {
      setLoading(false);
    }
  }

  function update(key: string, value: string) {
    setData((old) => ({ ...old, [key]: value }));
  }

  return (
    <main className="container">
      <section className="cv-hero">
        <Link href="/" className="back-link">← Volver a buscar empleo</Link>
        <h1>Asistente IA para tu CV</h1>
        <p>Te ayuda a ordenar tus datos, corregir errores y presentar mejor tus habilidades sin inventar información.</p>
      </section>

      <div className="cv-tabs" role="tablist" aria-label="Herramientas de CV">
        <button className={`filter-btn ${mode === 'generar' ? 'active' : ''}`} onClick={() => setMode('generar')}>Crear mi CV</button>
        <button className={`filter-btn ${mode === 'revisar' ? 'active' : ''}`} onClick={() => setMode('revisar')}>Corregir mi CV</button>
      </div>

      {mode === 'generar' ? (
        <section className="card cv-panel">
          <h2>Cuéntame sobre ti</h2>
          <p className="muted">No necesitas tener experiencia. Puedes dejar campos vacíos.</p>
          <div className="cv-form">
            {fields.map(([key, label]) => (
              <label key={key}>
                <span>{label}</span>
                {key === 'experiencia' || key === 'proyectos' || key === 'habilidades' || key === 'educacion' ? (
                  <textarea value={data[key] ?? ''} onChange={(e) => update(key, e.target.value)} placeholder={key === 'experiencia' ? 'Ej.: ayudé en el negocio familiar durante vacaciones...' : ''} />
                ) : (
                  <input value={data[key] ?? ''} onChange={(e) => update(key, e.target.value)} />
                )}
              </label>
            ))}
          </div>
          <button className="primary-btn cv-submit" onClick={() => void submit()} disabled={loading}>
            {loading ? 'Creando CV...' : 'Crear CV con IA'}
          </button>
        </section>
      ) : (
        <section className="card cv-panel">
          <h2>Pega tu CV</h2>
          <p className="muted">La IA revisará ortografía, claridad y orden, sin cambiar los hechos.</p>
          <textarea className="cv-large-textarea" value={texto} onChange={(e) => setTexto(e.target.value)} placeholder="Pega aquí el texto de tu CV..." />
          <button className="primary-btn cv-submit" onClick={() => void submit()} disabled={loading}>
            {loading ? 'Revisando...' : 'Corregir con IA'}
          </button>
        </section>
      )}

      {error && <div className="error" role="alert">{error}</div>}

      {result && (
        <section className="cv-results">
          <div className="card">
            <div className="section-head"><div><h2>Tu CV mejorado</h2><p>Revísalo antes de enviarlo.</p></div></div>
            <pre className="cv-output">{result.cv}</pre>
          </div>

          <div className="rights-grid">
            <article className="right-card">
              <h3>✅ Fortalezas</h3>
              {result.fortalezas.length ? <ul>{result.fortalezas.map((x, i) => <li key={i}>{x}</li>)}</ul> : <p className="muted">No se detectaron todavía.</p>}
            </article>
            <article className="right-card">
              <h3>✏️ Correcciones</h3>
              {result.correcciones.length ? <ul>{result.correcciones.map((x, i) => <li key={i}>{x}</li>)}</ul> : <p className="muted">No se detectaron correcciones importantes.</p>}
            </article>
          </div>

          {result.faltantes.length > 0 && (
            <article className="right-card cv-missing">
              <h3>📌 Podrías agregar</h3>
              <ul>{result.faltantes.map((x, i) => <li key={i}>{x}</li>)}</ul>
            </article>
          )}
        </section>
      )}

      <div className="notice">
        <strong>Privacidad:</strong> esta herramienta no necesita DNI, dirección exacta ni datos bancarios para ayudarte a crear un CV.
      </div>
    </main>
  );
}
