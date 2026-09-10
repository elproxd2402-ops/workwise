import Link from 'next/link';

export default function RightsStrip() {
  return (
    <section className="info-strip" aria-labelledby="rights-title">
      <h2 id="rights-title">Tus derechos a los 17</h2>
      <p>Jornada máxima de 6 horas, nada de trabajo nocturno, misma paga que una persona adulta por el mismo trabajo y derecho a denunciar ante SUNAFIL.</p>
      <Link href="/derechos" className="primary-btn">Ver mis derechos</Link>
    </section>
  );
}
