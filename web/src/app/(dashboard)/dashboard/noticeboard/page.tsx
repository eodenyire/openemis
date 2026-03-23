"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import api from "@/lib/api";
import { PageShell } from "@/components/shared/PageShell";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { DataTable, type Column } from "@/components/shared/DataTable";

interface Notice { id: number; title: string; content: string; target_audience: string; posted_date: string; active: boolean; }
interface BlogPost { id: number; title: string; category: string | null; author_id: number; published: boolean; created_at: string; }

const noticeCols: Column<Notice>[] = [
  { key: "title", header: "Title" },
  { key: "target_audience", header: "Audience", render: (r) => <Badge variant="outline">{r.target_audience}</Badge> },
  { key: "posted_date", header: "Posted", render: (r) => r.posted_date?.split("T")[0] ?? "—" },
  { key: "active", header: "Status", render: (r) => <Badge variant={r.active ? "default" : "secondary"}>{r.active ? "Active" : "Expired"}</Badge> },
];

const blogCols: Column<BlogPost>[] = [
  { key: "title", header: "Title" },
  { key: "category", header: "Category", render: (r) => r.category ?? "—" },
  { key: "published", header: "Status", render: (r) => <Badge variant={r.published ? "default" : "secondary"}>{r.published ? "Published" : "Draft"}</Badge> },
  { key: "created_at", header: "Created", render: (r) => r.created_at?.split("T")[0] ?? "—" },
];

export default function NoticeBoardPage() {
  const qc = useQueryClient();
  const [openNotice, setOpenNotice] = useState(false);
  const [openPost, setOpenPost] = useState(false);
  const [noticeForm, setNoticeForm] = useState({ title: "", content: "", target_audience: "all" });
  const [postForm, setPostForm] = useState({ title: "", content: "", published: false });

  const { data: notices, isLoading: loadingNotices } = useQuery({
    queryKey: ["notices"],
    queryFn: () => api.get<{ total: number; items: Notice[] }>("/noticeboard/notices").then((r) => r.data),
  });

  const { data: posts, isLoading: loadingPosts } = useQuery({
    queryKey: ["blog-posts"],
    queryFn: () => api.get<{ total: number; items: BlogPost[] }>("/blog/?published_only=false").then((r) => r.data),
  });

  const createNotice = useMutation({
    mutationFn: (b: object) => api.post("/noticeboard/notices", b),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["notices"] }); setOpenNotice(false); },
  });

  const createPost = useMutation({
    mutationFn: (b: object) => api.post("/blog/", b),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["blog-posts"] }); setOpenPost(false); },
  });

  return (
    <PageShell title="Notice Board & Blog" subtitle="School communications">
      <Tabs defaultValue="notices">
        <TabsList>
          <TabsTrigger value="notices">Notices ({notices?.total ?? 0})</TabsTrigger>
          <TabsTrigger value="blog">Blog Posts ({posts?.total ?? 0})</TabsTrigger>
        </TabsList>

        <TabsContent value="notices" className="space-y-4 mt-4">
          <div className="flex justify-end">
            <Button size="sm" onClick={() => setOpenNotice(true)}>+ Post Notice</Button>
          </div>
          <DataTable columns={noticeCols} data={notices?.items ?? []} loading={loadingNotices} keyField="id" emptyMessage="No notices posted." />
        </TabsContent>

        <TabsContent value="blog" className="space-y-4 mt-4">
          <div className="flex justify-end">
            <Button size="sm" onClick={() => setOpenPost(true)}>+ New Post</Button>
          </div>
          <DataTable columns={blogCols} data={posts?.items ?? []} loading={loadingPosts} keyField="id" emptyMessage="No blog posts." />
        </TabsContent>
      </Tabs>

      <Dialog open={openNotice} onOpenChange={setOpenNotice}>
        <DialogContent>
          <DialogHeader><DialogTitle>Post Notice</DialogTitle></DialogHeader>
          <div className="space-y-3">
            <div><Label>Title</Label><Input value={noticeForm.title} onChange={(e) => setNoticeForm({ ...noticeForm, title: e.target.value })} /></div>
            <div><Label>Content</Label><Input value={noticeForm.content} onChange={(e) => setNoticeForm({ ...noticeForm, content: e.target.value })} /></div>
            <div><Label>Audience</Label>
              <select className="w-full border rounded px-3 py-2 text-sm" value={noticeForm.target_audience}
                onChange={(e) => setNoticeForm({ ...noticeForm, target_audience: e.target.value })}>
                <option value="all">All</option><option value="students">Students</option>
                <option value="teachers">Teachers</option><option value="parents">Parents</option>
              </select>
            </div>
            <Button className="w-full" disabled={createNotice.isPending} onClick={() => createNotice.mutate(noticeForm)}>
              {createNotice.isPending ? "Posting..." : "Post"}
            </Button>
          </div>
        </DialogContent>
      </Dialog>

      <Dialog open={openPost} onOpenChange={setOpenPost}>
        <DialogContent>
          <DialogHeader><DialogTitle>New Blog Post</DialogTitle></DialogHeader>
          <div className="space-y-3">
            <div><Label>Title</Label><Input value={postForm.title} onChange={(e) => setPostForm({ ...postForm, title: e.target.value })} /></div>
            <div><Label>Content</Label><Input value={postForm.content} onChange={(e) => setPostForm({ ...postForm, content: e.target.value })} /></div>
            <Button className="w-full" disabled={createPost.isPending} onClick={() => createPost.mutate(postForm)}>
              {createPost.isPending ? "Saving..." : "Save Draft"}
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </PageShell>
  );
}
