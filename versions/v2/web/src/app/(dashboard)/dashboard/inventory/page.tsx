"use client";

import { useQuery } from "@tanstack/react-query";
import api from "@/lib/api";
import { PageShell } from "@/components/shared/PageShell";
import { DataTable, type Column } from "@/components/shared/DataTable";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

interface Item { id: number; name: string; code: string | null; category: string | null; quantity: number; unit: string | null; unit_price: number | null; low_stock: boolean; }
interface Transaction { id: number; item_name: string | null; type: string; quantity: number; date: string; reference: string | null; }

const itemCols: Column<Item>[] = [
  { key: "name", header: "Item" },
  { key: "code", header: "Code", render: (r) => r.code ?? "—" },
  { key: "category", header: "Category", render: (r) => r.category ?? "—" },
  { key: "quantity", header: "Qty" },
  { key: "unit", header: "Unit", render: (r) => r.unit ?? "—" },
  { key: "unit_price", header: "Unit Price", render: (r) => r.unit_price ? `KES ${r.unit_price}` : "—" },
  { key: "low_stock", header: "Stock", render: (r) => <Badge variant={r.low_stock ? "destructive" : "default"}>{r.low_stock ? "Low" : "OK"}</Badge> },
];

const txnCols: Column<Transaction>[] = [
  { key: "item_name", header: "Item", render: (r) => r.item_name ?? "—" },
  { key: "type", header: "Type", render: (r) => <Badge variant={r.type === "in" ? "default" : r.type === "out" ? "secondary" : "outline"}>{r.type}</Badge> },
  { key: "quantity", header: "Qty" },
  { key: "date", header: "Date" },
  { key: "reference", header: "Reference", render: (r) => r.reference ?? "—" },
];

export default function InventoryPage() {
  const { data: items, isLoading: loadingItems } = useQuery({
    queryKey: ["inventory-items"],
    queryFn: () => api.get<{ total: number; items: Item[] }>("/inventory/items").then(r => r.data),
  });
  const { data: txns, isLoading: loadingTxns } = useQuery({
    queryKey: ["inventory-txns"],
    queryFn: () => api.get<{ total: number; items: Transaction[] }>("/inventory/transactions").then(r => r.data),
  });

  return (
    <PageShell title="Inventory" subtitle="Stock items and transactions">
      <Tabs defaultValue="items">
        <TabsList>
          <TabsTrigger value="items">Items ({items?.total ?? 0})</TabsTrigger>
          <TabsTrigger value="transactions">Transactions ({txns?.total ?? 0})</TabsTrigger>
        </TabsList>
        <TabsContent value="items" className="mt-4">
          <DataTable columns={itemCols} data={items?.items ?? []} loading={loadingItems} keyField="id" emptyMessage="No items found." />
        </TabsContent>
        <TabsContent value="transactions" className="mt-4">
          <DataTable columns={txnCols} data={txns?.items ?? []} loading={loadingTxns} keyField="id" emptyMessage="No transactions found." />
        </TabsContent>
      </Tabs>
    </PageShell>
  );
}
