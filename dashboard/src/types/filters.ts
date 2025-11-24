/**
 * Tipos para los filtros globales del dashboard
 */

export interface DashboardFilters {
  startDate: Date | null;
  endDate: Date | null;
  departamento: string | null;
  estadoTelegram: "all" | "enviadas" | "pendientes";
}

export const DEFAULT_FILTERS: DashboardFilters = {
  startDate: null,
  endDate: null,
  departamento: null,
  estadoTelegram: "all",
};

