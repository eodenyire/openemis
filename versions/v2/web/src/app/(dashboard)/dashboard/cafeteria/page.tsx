"use client";

import { useQuery } from "@tanstack/react-query";
import api from "@/lib/api";
import { PageShell } from "@/components/shared/PageShell";
import { DataTable, type Column } from "@/components/shared/DataTable";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

interface MenuItem { id: number; name: string; category: string | null; price: number | null; description: string | null; active: boolean; }
interface DailyMenu { id: number; date: string; description: string | null; }

const itemCols: Column<MenuItem>[] = [
  { key: "name", header: "Item" },
  { key: "category", header: "Category", render: (r) => r.category ?? "—" },
  { key: "price", header: "Price", render: (r) => r.price ? `KES ${r.price}` : "—" },
  { key: "description", header: "Description", render: (r) => r.description ?? "—" },
  { key: "active", header: "Status", render: (r) => <Badge variant={r.active ? "default" : "secondary"}>{r.active ? "Active" : "Inactive"}</Badge> },
];

const menuCols: Column<DailyMenu>[] = [
  { key: "date", header: "Date" },
  { key: "description", header: "Menu", render: (r) => r.description ?? "—" },
];

export default function CafeteriaPage() {
  const { data: items, isLoading: loadingItems } = useQuery({
    queryKey: ["cafeteria-items"],
    queryFn: () => api.get<MenuItem[]>("/cafeteria/items").then(r => r.data),
  });
  const { data: menus, isLoading: loadingMenus } = useQuery({
    queryKey: ["cafeteria-menus"],
    queryFn: () => api.get<DailyMenu[]>("/cafeteria/daily-menu").then(r => r.data),
  });

  return (
    <PageShell title="Cafeteria" subtitle="Menu items and daily meal plans">
      <Tabs defaultValue="items">
        <TabsList>
          <TabsTrigger value="items">Menu Items</TabsTrigger>
          <TabsTrigger value="daily">Daily Menu</TabsTrigger>
        </TabsList>
        <TabsContent value="items" className="mt-4">
          <DataTable columns={itemCols} data={items ?? []} loading={loadingItems} keyField="id" emptyMessage="No menu items found." />
        </TabsContent>
        <TabsContent value="daily" className="mt-4">
          <DataTable columns={menuCols} data={menus ?? []} loading={loadingMenus} keyField="id" emptyMessage="No daily menus found." />
        </TabsContent>
      </Tabs>
    </PageShell>
  );
}
