import { useState, useEffect, useMemo } from "react";
import type { PQRS, PQRSStats, DepartmentChartData, TemporalChartData } from "@/types/pqrs";
import type { DashboardFilters } from "@/types/filters";
import {
  getPQRSData,
  calculateStats,
  getDepartmentChartData,
  getTemporalChartData,
  getCurrentMonthPQRS,
  getPreviousMonthPQRS,
  calculateMonthlyGrowth,
  filterByDateRange,
  filterByDepartment,
} from "@/utils/pqrs-utils";

interface UsePQRSDataReturn {
  pqrs: PQRS[];
  stats: PQRSStats | null;
  departmentData: DepartmentChartData[];
  temporalData: TemporalChartData[];
  currentMonthPQRS: PQRS[];
  previousMonthPQRS: PQRS[];
  monthlyGrowth: number;
  loading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
}

/**
 * Hook personalizado para obtener y procesar datos de PQRS
 */
export function usePQRSData(
  groupBy: "day" | "week" | "month" = "day",
  filters: DashboardFilters | null = null
): UsePQRSDataReturn {
  const [pqrs, setPqrs] = useState<PQRS[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getPQRSData();
      setPqrs(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al cargar datos");
      console.error("Error en usePQRSData:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  // Aplicar filtros a los datos
  const filteredPQRS = useMemo(() => {
    let filtered = [...pqrs];

    if (filters) {
      // Filtro por rango de fechas
      if (filters.startDate && filters.endDate) {
        filtered = filterByDateRange(filtered, filters.startDate, filters.endDate);
      }

      // Filtro por departamento
      if (filters.departamento) {
        filtered = filterByDepartment(filtered, filters.departamento);
      }

      // Filtro por estado de Telegram
      if (filters.estadoTelegram !== "all") {
        filtered = filtered.filter((item) => {
          if (filters.estadoTelegram === "enviadas") {
            return item.enviado_telegram === true;
          } else {
            return item.enviado_telegram === false;
          }
        });
      }
    }

    return filtered;
  }, [pqrs, filters]);

  const stats = filteredPQRS.length > 0 ? calculateStats(filteredPQRS) : null;
  const departmentData = filteredPQRS.length > 0 ? getDepartmentChartData(filteredPQRS) : [];
  const temporalData = filteredPQRS.length > 0 ? getTemporalChartData(filteredPQRS, groupBy) : [];
  const currentMonthPQRS = getCurrentMonthPQRS(filteredPQRS);
  const previousMonthPQRS = getPreviousMonthPQRS(filteredPQRS);
  const monthlyGrowth = calculateMonthlyGrowth(filteredPQRS);

  return {
    pqrs: filteredPQRS,
    stats,
    departmentData,
    temporalData,
    currentMonthPQRS,
    previousMonthPQRS,
    monthlyGrowth,
    loading,
    error,
    refetch: loadData,
  };
}

