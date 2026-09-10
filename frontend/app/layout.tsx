import type { Metadata } from 'next';
import Link from 'next/link';
import './globals.css';

export const metadata: Metadata = {
  title: 'WorkWise',
  description: 'Encuentra empresas y puestos que sean más claros y seguros para jóvenes en Perú.',
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="es">
      <body>
        <header className="site-header">
          <nav className="navbar" aria-label="Navegación principal">
            <Link href="/" className="brand" aria-label="WorkWise - inicio">
              <span className="brand-mark">TS</span>
              <span>WorkWise</span>
            </Link>
            <div className="nav-links">
              <Link href="/">Buscar trabajo</Link>
              <Link href="/derechos">Tus derechos</Link>
              <Link href="/cv">Asistente CV</Link>
            </div>
          </nav>
        </header>
        {children}
        <footer className="footer">
          <p>La puntuación es una guía informativa. Para un caso concreto, revisa la norma vigente y la información oficial de SUNAFIL.</p>
        </footer>
      </body>
    </html>
  );
}
