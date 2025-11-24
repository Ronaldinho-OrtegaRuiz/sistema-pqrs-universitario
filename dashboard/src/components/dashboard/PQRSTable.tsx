import {
  useReactTable,
  getCoreRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  flexRender,
  type ColumnDef,
  type SortingState,
} from "@tanstack/react-table";
import { useState } from "react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { usePQRSData } from "@/hooks/usePQRSData";
import type { PQRS } from "@/types/pqrs";
import type { DashboardFilters } from "@/types/filters";
import { CheckCircle2, XCircle, ChevronLeft, ChevronRight } from "lucide-react";

interface PQRSTableProps {
  filters: DashboardFilters;
}

export function PQRSTable({ filters }: PQRSTableProps) {
  const { pqrs, loading } = usePQRSData("day", filters);
  const [sorting, setSorting] = useState<SortingState>([]);

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString("es-ES", {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  };

  const columns: ColumnDef<PQRS>[] = [
    {
      accessorKey: "pqrs_id",
      header: "ID",
      cell: ({ row }) => (
        <div className="font-mono text-xs">{row.getValue("pqrs_id")}</div>
      ),
    },
    {
      accessorKey: "departamento",
      header: "Departamento",
      cell: ({ row }) => (
        <div className="font-medium">{row.getValue("departamento")}</div>
      ),
    },
    {
      accessorKey: "descripcion",
      header: "Descripción",
      cell: ({ row }) => {
        const descripcion = row.getValue("descripcion") as string;
        return (
          <div className="max-w-[300px] truncate" title={descripcion}>
            {descripcion}
          </div>
        );
      },
    },
    {
      accessorKey: "fecha_registro",
      header: "Fecha de Registro",
      cell: ({ row }) => formatDate(row.getValue("fecha_registro")),
    },
    {
      accessorKey: "enviado_telegram",
      header: "Estado Telegram",
      cell: ({ row }) => {
        const enviado = row.getValue("enviado_telegram") as boolean;
        return (
          <div className="flex items-center gap-2">
            {enviado ? (
              <>
                <CheckCircle2 className="h-4 w-4 text-green-600" />
                <span className="text-sm text-green-600">Enviada</span>
              </>
            ) : (
              <>
                <XCircle className="h-4 w-4 text-orange-600" />
                <span className="text-sm text-orange-600">Pendiente</span>
              </>
            )}
          </div>
        );
      },
    },
  ];

  const table = useReactTable({
    data: pqrs,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    getSortedRowModel: getSortedRowModel(),
    onSortingChange: setSorting,
    state: {
      sorting,
    },
    initialState: {
      pagination: {
        pageSize: 10,
      },
    },
  });

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Tabla de PQRS</CardTitle>
          <CardDescription>Listado de todas las solicitudes</CardDescription>
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
        <CardTitle>Tabla de PQRS</CardTitle>
        <CardDescription>
          Listado de todas las solicitudes ({pqrs.length} registros)
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="rounded-md border overflow-x-auto">
          <Table>
            <TableHeader>
              {table.getHeaderGroups().map((headerGroup) => (
                <TableRow key={headerGroup.id}>
                  {headerGroup.headers.map((header) => (
                    <TableHead
                      key={header.id}
                      className={
                        header.column.getCanSort()
                          ? "cursor-pointer select-none hover:bg-muted/50"
                          : ""
                      }
                      onClick={header.column.getToggleSortingHandler()}
                    >
                      {header.isPlaceholder
                        ? null
                        : flexRender(
                            header.column.columnDef.header,
                            header.getContext()
                          )}
                      {header.column.getIsSorted() === "asc" && " ↑"}
                      {header.column.getIsSorted() === "desc" && " ↓"}
                    </TableHead>
                  ))}
                </TableRow>
              ))}
            </TableHeader>
            <TableBody>
              {table.getRowModel().rows?.length ? (
                table.getRowModel().rows.map((row) => (
                  <TableRow
                    key={row.id}
                    data-state={row.getIsSelected() && "selected"}
                  >
                    {row.getVisibleCells().map((cell) => (
                      <TableCell key={cell.id}>
                        {flexRender(
                          cell.column.columnDef.cell,
                          cell.getContext()
                        )}
                      </TableCell>
                    ))}
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell
                    colSpan={columns.length}
                    className="h-24 text-center"
                  >
                    No se encontraron resultados.
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </div>
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 px-2 py-4">
          <div className="text-sm text-muted-foreground text-center sm:text-left">
            Mostrando{" "}
            {table.getState().pagination.pageIndex *
              table.getState().pagination.pageSize +
              1}{" "}
            a{" "}
            {Math.min(
              (table.getState().pagination.pageIndex + 1) *
                table.getState().pagination.pageSize,
              pqrs.length
            )}{" "}
            de {pqrs.length} registros
          </div>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => table.previousPage()}
              disabled={!table.getCanPreviousPage()}
            >
              <ChevronLeft className="h-4 w-4" />
            </Button>
            <div className="text-sm font-medium whitespace-nowrap">
              Página {table.getState().pagination.pageIndex + 1} de{" "}
              {table.getPageCount()}
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={() => table.nextPage()}
              disabled={!table.getCanNextPage()}
            >
              <ChevronRight className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

