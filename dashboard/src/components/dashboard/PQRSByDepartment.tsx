import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
} from "@/components/ui/chart";
import { usePQRSData } from "@/hooks/usePQRSData";
import { Bar, BarChart, CartesianGrid, XAxis, YAxis } from "recharts";
import type { DashboardFilters } from "@/types/filters";

interface PQRSByDepartmentProps {
  filters: DashboardFilters;
}

const chartConfig = {
  cantidad: {
    label: "Cantidad",
    color: "var(--chart-1)",
  },
  enviadas: {
    label: "Enviadas",
    color: "var(--chart-2)",
  },
  pendientes: {
    label: "Pendientes",
    color: "var(--chart-3)",
  },
} satisfies import("@/components/ui/chart").ChartConfig;

export function PQRSByDepartment({ filters }: PQRSByDepartmentProps) {
  const { departmentData, loading } = usePQRSData("day", filters);

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>PQRS por Departamento</CardTitle>
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
        <CardTitle>PQRS por Departamento</CardTitle>
        <CardDescription>
          Distribución de solicitudes por área
        </CardDescription>
      </CardHeader>
      <CardContent>
        <ChartContainer config={chartConfig}>
          <BarChart
            data={departmentData}
            margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              dataKey="departamento"
              angle={-45}
              textAnchor="end"
              height={100}
              tick={{ fontSize: 12 }}
            />
            <YAxis tick={{ fontSize: 12 }} />
            <ChartTooltip content={<ChartTooltipContent />} />
            <Bar
              dataKey="cantidad"
              fill="var(--color-cantidad)"
              radius={[4, 4, 0, 0]}
            />
          </BarChart>
        </ChartContainer>
      </CardContent>
    </Card>
  );
}

