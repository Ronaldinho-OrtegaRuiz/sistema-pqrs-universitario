/**
 * Tipos TypeScript para las PQRS del sistema
 */

export interface PQRS {
  pqrs_id: string;
  departamento: string;
  codigo_departamento: string;
  descripcion: string;
  fecha: string;
  telefono: string;
  enviado_telegram: boolean;
  fecha_registro: string;
  fecha_envio_telegram?: string;
}

/**
 * Códigos de departamento disponibles
 */
export const DEPARTAMENTOS = {
  TEC: "Tecnología",
  ASE: "Aseo y Mantenimiento",
  EDU: "Educativo",
  ADM: "Administrativo",
  BIB: "Biblioteca",
  SEG: "Seguridad",
  OTR: "Otro",
} as const;

export type CodigoDepartamento = keyof typeof DEPARTAMENTOS;

/**
 * Estadísticas agregadas para gráficas
 */
export interface PQRSStats {
  total: number;
  porDepartamento: Record<string, number>;
  porMes: Record<string, number>;
  enviadasTelegram: number;
  pendientesTelegram: number;
  tendenciaMensual: Array<{
    mes: string;
    cantidad: number;
  }>;
}

/**
 * Datos para gráfica de barras por departamento
 */
export interface DepartmentChartData {
  departamento: string;
  cantidad: number;
  enviadas: number;
  pendientes: number;
}

/**
 * Datos para gráfica temporal
 */
export interface TemporalChartData {
  fecha: string;
  cantidad: number;
  acumulado: number;
}

