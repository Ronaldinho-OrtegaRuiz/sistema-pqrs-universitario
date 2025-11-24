import { CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { MagicCard } from "@/components/ui/magic-card";
import { usePQRSData } from "@/hooks/usePQRSData";
import { TrendingUp, TrendingDown, FileText, Send } from "lucide-react";
import { NumberTicker } from "../ui/number-ticker";
import type { DashboardFilters } from "@/types/filters";

interface KPIStatsProps {
  filters: DashboardFilters;
}

export function KPIStats({ filters }: KPIStatsProps) {
  const { stats, currentMonthPQRS, monthlyGrowth, loading } =
    usePQRSData("day", filters);

  if (loading || !stats) {
    return (
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {[...Array(4)].map((_, i) => (
          <MagicCard key={i}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Cargando...</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">-</div>
            </CardContent>
          </MagicCard>
        ))}
      </div>
    );
  }

  const growthIcon = monthlyGrowth >= 0 ? TrendingUp : TrendingDown;
  const GrowthIcon = growthIcon;
  const growthColor = monthlyGrowth >= 0 ? "text-green-600" : "text-red-600";

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      {/* Total de PQRS */}
      <MagicCard>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Total de PQRS</CardTitle>
          <FileText className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <NumberTicker className="text-2xl font-bold" value={stats.total}/>
          <p className="text-xs text-muted-foreground">
            Registros totales en el sistema
          </p>
        </CardContent>
      </MagicCard>

      {/* PQRS del mes actual */}
      <MagicCard>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">PQRS del Mes</CardTitle>
          <FileText className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{currentMonthPQRS.length}</div>
          <div className="flex items-center gap-1 text-xs">
            <GrowthIcon className={`h-3 w-3 ${growthColor}`} />
            <span className={growthColor}>
              {Math.abs(monthlyGrowth).toFixed(1)}%
            </span>
            <span className="text-muted-foreground">vs mes anterior</span>
          </div>
        </CardContent>
      </MagicCard>

      {/* PQRS pendientes */}
      <MagicCard>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Pendientes</CardTitle>
          <FileText className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
        <NumberTicker className="text-2xl font-bold" value={stats.pendientesTelegram}/>
          <p className="text-xs text-muted-foreground">
            Sin enviar a Telegram
          </p>
        </CardContent>
      </MagicCard>

      {/* PQRS enviadas */}
      <MagicCard>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Enviadas</CardTitle>
          <Send className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
        <NumberTicker className="text-2xl font-bold" value={stats.enviadasTelegram}/>
          <p className="text-xs text-muted-foreground">
            Enviadas a Telegram
          </p>
        </CardContent>
      </MagicCard>
    </div>
  );
}

