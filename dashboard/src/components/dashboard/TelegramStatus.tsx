import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
  ChartLegend,
  ChartLegendContent,
} from "@/components/ui/chart";
import { usePQRSData } from "@/hooks/usePQRSData";
import { Bar, BarChart, CartesianGrid, XAxis, YAxis } from "recharts";
import type { DashboardFilters } from "@/types/filters";

interface TelegramStatusProps {
  filters: DashboardFilters;
}

const chartConfig = {
  enviadas: {
    label: "Enviadas",
    color: "var(--chart-1)",
  },
  pendientes: {
    label: "Pendientes",
    color: "var(--chart-2)",
  },
} satisfies import("@/components/ui/chart").ChartConfig;

export function TelegramStatus({ filters }: TelegramStatusProps) {
  const { departmentData, loading } = usePQRSData("day", filters);

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Estado de Envío a Telegram</CardTitle>
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
        <CardTitle>Estado de Envío a Telegram</CardTitle>
        <CardDescription>
          PQRS enviadas vs pendientes por departamento
        </CardDescription>
      </CardHeader>
      <CardContent>
        <ChartContainer config={chartConfig}>
          <BarChart
            accessibilityLayer
            data={departmentData}
            margin={{
              left: 12,
              right: 12,
            }}
          >
            <CartesianGrid vertical={false} />
            <XAxis
              dataKey="departamento"
              tickLine={false}
              axisLine={false}
              tickMargin={8}
              tickFormatter={(value) => {
                // Acortar nombres largos para móviles
                if (value.length > 15) {
                  return value.slice(0, 12) + "..."
                }
                return value
              }}
            />
            <ChartTooltip
              cursor={false}
              content={<ChartTooltipContent />}
            />
            <ChartLegend content={<ChartLegendContent />} />
            <Bar
              dataKey="enviadas"
              stackId="a"
              fill="var(--color-enviadas)"
              radius={[0, 0, 0, 0]}
            />
            <Bar
              dataKey="pendientes"
              stackId="a"
              fill="var(--color-pendientes)"
              radius={[4, 4, 0, 0]}
            />
          </BarChart>
        </ChartContainer>
      </CardContent>
    </Card>
  );
}

