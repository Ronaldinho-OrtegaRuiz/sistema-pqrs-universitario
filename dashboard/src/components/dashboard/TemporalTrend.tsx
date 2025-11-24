import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
} from "@/components/ui/chart";
import { usePQRSData } from "@/hooks/usePQRSData";
import { Area, AreaChart, CartesianGrid, XAxis, YAxis } from "recharts";
import type { DashboardFilters } from "@/types/filters";

interface TemporalTrendProps {
  filters: DashboardFilters;
}

const chartConfig = {
  cantidad: {
    label: "PQRS",
    color: "var(--chart-1)",
  },
  acumulado: {
    label: "Acumulado",
    color: "var(--chart-2)",
  },
} satisfies import("@/components/ui/chart").ChartConfig;

export function TemporalTrend({ filters }: TemporalTrendProps) {
  const { temporalData, loading } = usePQRSData("day", filters);

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Tendencia Temporal</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex h-[300px] items-center justify-center">
            <p className="text-sm text-muted-foreground">Cargando datos...</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Tendencia Temporal</CardTitle>
        <CardDescription>
          Evolución de PQRS a lo largo del tiempo
        </CardDescription>
      </CardHeader>
      <CardContent>
        <ChartContainer config={chartConfig}>
          <AreaChart
            data={temporalData}
            margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
          >
            <defs>
              <linearGradient id="fillCantidad" x1="0" y1="0" x2="0" y2="1">
                <stop
                  offset="5%"
                  stopColor="var(--color-cantidad)"
                  stopOpacity={0.8}
                />
                <stop
                  offset="95%"
                  stopColor="var(--color-cantidad)"
                  stopOpacity={0.1}
                />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              dataKey="fecha"
              tick={{ fontSize: 12 }}
              angle={-45}
              textAnchor="end"
              height={80}
            />
            <YAxis tick={{ fontSize: 12 }} />
            <ChartTooltip content={<ChartTooltipContent />} />
            <Area
              type="monotone"
              dataKey="cantidad"
              stroke="var(--color-cantidad)"
              fill="url(#fillCantidad)"
            />
          </AreaChart>
        </ChartContainer>
      </CardContent>
    </Card>
  );
}

