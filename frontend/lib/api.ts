export type EmpresaCard = {
  id: number;
  nombre: string;
  sector: string | null;
  ciudad: string | null;
  puntaje: number;
  semaforo: 'verde' | 'amarillo' | 'rojo';
  resumen_ia: string;
  exige_titulo: boolean;
  apto_joven: boolean;
  sanciones: number;
  ofertas_cortas: number;
  distancia_km: number | null;
  es_demo: boolean;
};

export type Resena = {
  id: number;
  texto: string;
  rating: number;
  fecha: string | null;
  fuente: string | null;
  url_fuente: string | null;
};

export type Sancion = {
  id: number;
  tipo: string;
  fecha: string | null;
  fuente: string | null;
  url_fuente: string | null;
};

export type Oferta = {
  id: number;
  titulo_puesto: string;
  descripcion: string | null;
  requiere_titulo: boolean;
  jornada_horas: number | null;
  apto_joven: boolean;
  alertas: string | null;
  url_aplicacion: string | null;
};

export type EmpresaDetail = EmpresaCard & {
  actualizado_ia: string | null;
  reputacion: number;
  cumplimiento: number;
  elegibilidad_juvenil: number;
  facil_aplicar: number;
  resenas: Resena[];
  sanciones_detalle: Sancion[];
  ofertas: Oferta[];
};

const API = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API}${path}`, {
    ...init,
    headers: { 'Content-Type': 'application/json', ...(init?.headers ?? {}) },
    cache: 'no-store',
  });
  if (!response.ok) {
    let detail = `Error ${response.status}`;
    try {
      const body = await response.json();
      detail = body.detail ?? detail;
    } catch {}
    throw new Error(detail);
  }
  return response.json();
}

export async function getEmpresas(params: Record<string, string | number | boolean | undefined> = {}) {
  const qs = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== '' && value !== false) qs.set(key, String(value));
  }
  return request<EmpresaCard[]>(`/empresas${qs.toString() ? `?${qs}` : ''}`);
}

export async function getEmpresa(id: number) {
  return request<EmpresaDetail>(`/empresas/${id}`);
}

export async function regenerateSummary(id: number) {
  return request<{ id: number; resumen_ia: string; actualizado_ia: string }>(`/empresas/${id}/regenerar_resumen`, {
    method: 'POST',
  });
}


export type CVResponse = {
  cv: string;
  correcciones: string[];
  fortalezas: string[];
  faltantes: string[];
};

export async function asistenteCV(payload: {
  accion: 'generar' | 'revisar';
  datos?: Record<string, string>;
  texto_cv?: string;
}) {
  return request<CVResponse>('/ia/cv', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}
