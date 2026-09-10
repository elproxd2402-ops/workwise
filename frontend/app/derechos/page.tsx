import Link from 'next/link';

export default function DerechosPage() {
  return (
    <main className="container">
      <section className="hero">
        <Link href="/" className="back-link">← Volver</Link>
        <h1>Tus derechos a los 17</h1>
        <p>Una guía simple para revisar antes de aceptar un empleo. La información es orientativa y debes revisar la norma vigente en tu caso.</p>
      </section>

      <div className="rights-grid">
        <article className="right-card"><h3>⏱️ Jornada</h3><p>Para una persona de 17 años, la web usa como regla de filtro una jornada máxima de 6 horas al día.</p></article>
        <article className="right-card"><h3>🌙 Trabajo nocturno</h3><p>La web marca como no aptos para 17 años los puestos con trabajo nocturno.</p></article>
        <article className="right-card"><h3>💰 Pago</h3><p>La guía presenta como principio de referencia que el trabajo de una persona adolescente debe respetar su remuneración laboral, sin asumir que por ser menor vale menos.</p></article>
        <article className="right-card"><h3>🛡️ Seguridad</h3><p>Un puesto no debe exponerte a actividades prohibidas o peligrosas. Revisa siempre las funciones reales del puesto.</p></article>
        <article className="right-card"><h3>📣 Denunciar</h3><p>Cuando exista un posible incumplimiento laboral, puedes acudir a SUNAFIL y revisar sus canales oficiales de atención y denuncia.</p></article>
        <article className="right-card"><h3>📚 Base legal</h3><p>El proyecto toma como referencias la Ley 27337 y la Ley 30288. Las reglas se mantienen separadas en el backend para poder actualizarse con cambios normativos.</p></article>
      </div>

      <div className="notice">
        <strong>Importante:</strong> “Apto para joven” en esta web no reemplaza una evaluación legal. En especial, una persona de 18 a 20 años ya no se encuentra en la misma categoría jurídica que una persona de 17.
      </div>
    </main>
  );
}
