import { useState } from "react";
import { KPIStats } from "@/components/dashboard/KPIStats";
import { PQRSByDepartment } from "@/components/dashboard/PQRSByDepartment";
import { TemporalTrend } from "@/components/dashboard/TemporalTrend";
import { DepartmentDistribution } from "@/components/dashboard/DepartmentDistribution";
import { TelegramStatus } from "@/components/dashboard/TelegramStatus";
import { DashboardFilters } from "@/components/dashboard/DashboardFilters";
import { PQRSTable } from "@/components/dashboard/PQRSTable";
import { AnimatedThemeToggler } from "@/components/ui/animated-theme-toggler";
import logoFull from "@/assets/logo-full.webp";
import { DEFAULT_FILTERS } from "@/types/filters";
import type { DashboardFilters as DashboardFiltersType } from "@/types/filters";

export function Dashboard() {
  const [filters, setFilters] = useState<DashboardFiltersType>(DEFAULT_FILTERS);

  return (
    <div className="flex-1 space-y-4 p-0 md:p-8">
      <div className="flex items-center justify-between w-full">
        {/* ThemeToggle a la izquierda */}
        <div className="shrink-0 min-w-[120px] flex justify-start">
          <AnimatedThemeToggler className="h-9 w-9 rounded-md border border-input bg-background hover:bg-accent hover:text-accent-foreground flex items-center justify-center" />
        </div>
        
        {/* Logo en el centro */}
        <div className="flex-1 flex justify-center min-w-0">
          <img 
            src={logoFull} 
            alt="Logo Universidad Los Libertadores" 
            className="h-16 md:h-24 object-contain dark:brightness-200"
          />
        </div>
        
        {/* Párrafo a la derecha */}
        <div className="shrink-0 min-w-[120px] flex justify-end text-right">
          <p className="text-sm md:text-base text-muted-foreground">
            Sistema de PQRS
          </p>
        </div>
      </div>

      {/* Filtros Globales */}
      <DashboardFilters filters={filters} onFiltersChange={setFilters} />

      {/* KPIs */}
      <KPIStats filters={filters} />

      {/* Gráficas principales */}
      <div className="grid gap-4 md:grid-cols-2">
        <TemporalTrend filters={filters} />
        <PQRSByDepartment filters={filters} />
      </div>

      {/* Gráficas secundarias */}
      <div className="grid gap-4 md:grid-cols-2">
        <DepartmentDistribution filters={filters} />
        <TelegramStatus filters={filters} />
      </div>

      {/* Tabla de PQRS */}
      <PQRSTable filters={filters} />
    </div>
  );
}

