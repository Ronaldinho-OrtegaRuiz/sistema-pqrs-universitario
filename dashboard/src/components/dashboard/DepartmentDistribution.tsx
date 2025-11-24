import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
  ChartLegend,
  ChartLegendContent,
} from "@/components/ui/chart";
import { usePQRSData } from "@/hooks/usePQRSData";
import { Pie, PieChart, Cell } from "recharts";
import type { DashboardFilters } from "@/types/filters";

interface DepartmentDistributionProps {
  filters: DashboardFilters;
}

const COLORS = [
  "var(--chart-1)",
  "var(--chart-2)",
  "var(--chart-3)",
  "var(--chart-4)",
  "var(--chart-5)",
  "var(--chart-6)",
  "var(--chart-7)",
];

const chartConfig = {
  cantidad: {
    label: "Cantidad",
  },
} satisfies import("@/components/ui/chart").ChartConfig;

export function DepartmentDistribution({ filters }: DepartmentDistributionProps) {
  const { departmentData, loading } = usePQRSData("day", filters);

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Distribución por Departamento</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex h-[300px] items-center justify-center">
            <p className="text-sm text-muted-foreground">Cargando datos...</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  // Preparar datos para el gráfico de pastel
  const pieData = departmentData.map((item) => ({
    name: item.departamento,
    value: item.cantidad,
  }));

  return (
    <Card>
      <CardHeader>
        <CardTitle>Distribución por Departamento</CardTitle>
        <CardDescription>
          Porcentaje de PQRS por área
        </CardDescription>
      </CardHeader>
      <CardContent>
        <ChartContainer config={chartConfig}>
          <PieChart>
            <ChartTooltip
              content={<ChartTooltipContent hideLabel />}
              cursor={false}
            />
            <Pie
              data={pieData}
              dataKey="value"
              nameKey="name"
              cx="50%"
              cy="50%"
              outerRadius="60%"
              label={({ name, percent }) =>
                `${name}: ${(percent * 100).toFixed(0)}%`
              }
            >
              {pieData.map((_, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={COLORS[index % COLORS.length]}
                />
              ))}
            </Pie>
            <ChartLegend
              content={<ChartLegendContent nameKey="name" />}
              className="-bottom-2"
            />
          </PieChart>
        </ChartContainer>
      </CardContent>
    </Card>
  );
}

