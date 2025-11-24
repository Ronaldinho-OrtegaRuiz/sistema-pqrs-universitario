/**
 * Utilidades para procesar y transformar datos de PQRS
 */
import type { PQRS, DepartmentChartData, TemporalChartData, PQRSStats } from "@/types/pqrs";
import pqrsData from "@/data/pqrs-data.json";

/**
 * Obtiene todas las PQRS desde el archivo JSON
 * En producción, esto debería hacer una llamada a la API
 */
export async function getPQRSData(): Promise<PQRS[]> {
  try {
    // En desarrollo, usar datos estáticos
    // En producción, reemplazar con llamada a API: const response = await fetch("/api/pqrs");
    return pqrsData as PQRS[];
  } catch (error) {
    console.error("Error al cargar datos de PQRS:", error);
    return [];
  }
}

/**
 * Calcula estadísticas generales de las PQRS
 */
export function calculateStats(pqrs: PQRS[]): PQRSStats {
  const porDepartamento: Record<string, number> = {};
  const porMes: Record<string, number> = {};
  let enviadasTelegram = 0;
  let pendientesTelegram = 0;

  pqrs.forEach((item) => {
    // Contar por departamento
    const dept = item.departamento;
    porDepartamento[dept] = (porDepartamento[dept] || 0) + 1;

    // Contar por mes
    const fecha = new Date(item.fecha_registro);
    const mesKey = `${fecha.getFullYear()}-${String(fecha.getMonth() + 1).padStart(2, "0")}`;
    porMes[mesKey] = (porMes[mesKey] || 0) + 1;

    // Contar estado de Telegram
    if (item.enviado_telegram) {
      enviadasTelegram++;
    } else {
      pendientesTelegram++;
    }
  });

  // Generar tendencia mensual ordenada
  const tendenciaMensual = Object.entries(porMes)
    .map(([mes, cantidad]) => ({
      mes,
      cantidad,
    }))
    .sort((a, b) => a.mes.localeCompare(b.mes));

  return {
    total: pqrs.length,
    porDepartamento,
    porMes,
    enviadasTelegram,
    pendientesTelegram,
    tendenciaMensual,
  };
}

/**
 * Genera datos para gráfica de barras por departamento
 */
export function getDepartmentChartData(pqrs: PQRS[]): DepartmentChartData[] {
  const deptMap = new Map<string, { total: number; enviadas: number; pendientes: number }>();

  pqrs.forEach((item) => {
    const dept = item.departamento;
    if (!deptMap.has(dept)) {
      deptMap.set(dept, { total: 0, enviadas: 0, pendientes: 0 });
    }

    const stats = deptMap.get(dept)!;
    stats.total++;
    if (item.enviado_telegram) {
      stats.enviadas++;
    } else {
      stats.pendientes++;
    }
  });

  return Array.from(deptMap.entries())
    .map(([departamento, stats]) => ({
      departamento,
      cantidad: stats.total,
      enviadas: stats.enviadas,
      pendientes: stats.pendientes,
    }))
    .sort((a, b) => b.cantidad - a.cantidad);
}

/**
 * Genera datos para gráfica temporal (líneas o área)
 */
export function getTemporalChartData(
  pqrs: PQRS[],
  groupBy: "day" | "week" | "month" = "day"
): TemporalChartData[] {
  const dateMap = new Map<string, number>();

  pqrs.forEach((item) => {
    const fecha = new Date(item.fecha_registro);
    let key: string;

    if (groupBy === "day") {
      key = fecha.toISOString().split("T")[0]; // YYYY-MM-DD
    } else if (groupBy === "week") {
      const weekStart = new Date(fecha);
      weekStart.setDate(fecha.getDate() - fecha.getDay());
      key = weekStart.toISOString().split("T")[0];
    } else {
      // month
      key = `${fecha.getFullYear()}-${String(fecha.getMonth() + 1).padStart(2, "0")}`;
    }

    dateMap.set(key, (dateMap.get(key) || 0) + 1);
  });

  const data = Array.from(dateMap.entries())
    .map(([fecha, cantidad]) => ({
      fecha,
      cantidad,
      acumulado: 0, // Se calculará después
    }))
    .sort((a, b) => a.fecha.localeCompare(b.fecha));

  // Calcular acumulado
  let acumulado = 0;
  return data.map((item) => {
    acumulado += item.cantidad;
    return {
      ...item,
      acumulado,
    };
  });
}

/**
 * Filtra PQRS por rango de fechas
 */
export function filterByDateRange(
  pqrs: PQRS[],
  startDate: Date,
  endDate: Date
): PQRS[] {
  return pqrs.filter((item) => {
    const fecha = new Date(item.fecha_registro);
    return fecha >= startDate && fecha <= endDate;
  });
}

/**
 * Filtra PQRS por departamento
 */
export function filterByDepartment(
  pqrs: PQRS[],
  codigoDepartamento: string
): PQRS[] {
  return pqrs.filter(
    (item) => item.codigo_departamento === codigoDepartamento
  );
}

/**
 * Obtiene PQRS del mes actual
 */
export function getCurrentMonthPQRS(pqrs: PQRS[]): PQRS[] {
  const now = new Date();
  const startOfMonth = new Date(now.getFullYear(), now.getMonth(), 1);
  const endOfMonth = new Date(now.getFullYear(), now.getMonth() + 1, 0, 23, 59, 59);

  return filterByDateRange(pqrs, startOfMonth, endOfMonth);
}

/**
 * Obtiene PQRS del mes anterior
 */
export function getPreviousMonthPQRS(pqrs: PQRS[]): PQRS[] {
  const now = new Date();
  const startOfPreviousMonth = new Date(now.getFullYear(), now.getMonth() - 1, 1);
  const endOfPreviousMonth = new Date(now.getFullYear(), now.getMonth(), 0, 23, 59, 59);

  return filterByDateRange(pqrs, startOfPreviousMonth, endOfPreviousMonth);
}

/**
 * Calcula la tasa de crecimiento mensual
 */
export function calculateMonthlyGrowth(pqrs: PQRS[]): number {
  const currentMonth = getCurrentMonthPQRS(pqrs).length;
  const previousMonth = getPreviousMonthPQRS(pqrs).length;

  if (previousMonth === 0) {
    return currentMonth > 0 ? 100 : 0;
  }

  return ((currentMonth - previousMonth) / previousMonth) * 100;
}

