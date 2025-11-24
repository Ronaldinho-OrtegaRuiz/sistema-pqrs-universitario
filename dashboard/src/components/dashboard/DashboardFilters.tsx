import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { X, Filter } from "lucide-react";
import type { DashboardFilters } from "@/types/filters";
import { DEPARTAMENTOS } from "@/types/pqrs";
import { DEFAULT_FILTERS } from "@/types/filters";

interface DashboardFiltersProps {
  filters: DashboardFilters;
  onFiltersChange: (filters: DashboardFilters) => void;
}

export function DashboardFilters({
  filters,
  onFiltersChange,
}: DashboardFiltersProps) {
  const [localFilters, setLocalFilters] = useState<DashboardFilters>(filters);

  // Sincronizar filtros locales con los props cuando cambien externamente
  useEffect(() => {
    setLocalFilters(filters);
  }, [filters]);

  const handleFilterChange = (key: keyof DashboardFilters, value: any) => {
    const newFilters = { ...localFilters, [key]: value };
    setLocalFilters(newFilters);
    onFiltersChange(newFilters);
  };

  const handleClearFilters = () => {
    setLocalFilters(DEFAULT_FILTERS);
    onFiltersChange(DEFAULT_FILTERS);
  };

  const hasActiveFilters =
    localFilters.startDate ||
    localFilters.endDate ||
    localFilters.departamento ||
    localFilters.estadoTelegram !== "all";

  // Formatear fecha para input type="date"
  const formatDateForInput = (date: Date | null): string => {
    if (!date) return "";
    const d = new Date(date);
    d.setMinutes(d.getMinutes() - d.getTimezoneOffset());
    return d.toISOString().split("T")[0];
  };

  // Convertir string de fecha a Date
  const parseDateFromInput = (dateString: string): Date | null => {
    if (!dateString) return null;
    const date = new Date(dateString);
    date.setHours(0, 0, 0, 0);
    return date;
  };

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4">
        <CardTitle className="text-lg font-semibold flex items-center gap-2">
          <Filter className="h-5 w-5" />
          Filtros
        </CardTitle>
        {hasActiveFilters && (
          <Button
            variant="ghost"
            size="sm"
            onClick={handleClearFilters}
            className="h-8 w-8 p-0"
          >
            <X className="h-4 w-4" />
          </Button>
        )}
      </CardHeader>
      <CardContent>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {/* Filtro por fecha inicial */}
          <div className="space-y-2">
            <Label htmlFor="startDate">Fecha Inicial</Label>
            <Input
              id="startDate"
              type="date"
              value={formatDateForInput(localFilters.startDate)}
              onChange={(e) =>
                handleFilterChange("startDate", parseDateFromInput(e.target.value))
              }
            />
          </div>

          {/* Filtro por fecha final */}
          <div className="space-y-2">
            <Label htmlFor="endDate">Fecha Final</Label>
            <Input
              id="endDate"
              type="date"
              value={formatDateForInput(localFilters.endDate)}
              onChange={(e) =>
                handleFilterChange("endDate", parseDateFromInput(e.target.value))
              }
              min={formatDateForInput(localFilters.startDate)}
            />
          </div>

          {/* Filtro por departamento */}
          <div className="space-y-2">
            <Label htmlFor="departamento">Departamento</Label>
            <Select
              value={localFilters.departamento || "all"}
              onValueChange={(value) =>
                handleFilterChange("departamento", value === "all" ? null : value)
              }
            >
              <SelectTrigger id="departamento">
                <SelectValue placeholder="Todos los departamentos" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Todos los departamentos</SelectItem>
                {Object.entries(DEPARTAMENTOS).map(([codigo, nombre]) => (
                  <SelectItem key={codigo} value={codigo}>
                    {nombre}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Filtro por estado de Telegram */}
          <div className="space-y-2">
            <Label htmlFor="estadoTelegram">Estado Telegram</Label>
            <Select
              value={localFilters.estadoTelegram}
              onValueChange={(value: "all" | "enviadas" | "pendientes") =>
                handleFilterChange("estadoTelegram", value)
              }
            >
              <SelectTrigger id="estadoTelegram">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Todos</SelectItem>
                <SelectItem value="enviadas">Enviadas</SelectItem>
                <SelectItem value="pendientes">Pendientes</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

