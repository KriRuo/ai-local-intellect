import React from "react";
import { useNavigate, useParams } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { AlertDialog, AlertDialogTrigger, AlertDialogContent, AlertDialogHeader, AlertDialogTitle, AlertDialogDescription, AlertDialogFooter, AlertDialogCancel, AlertDialogAction } from "@/components/ui/alert-dialog";
import { toast } from "sonner";

interface Note {
  id: number;
  title: string;
  description?: string;
  created_at: string;
  updated_at?: string;
}

interface NoteEditProps {
  mode: "create" | "edit";
}

const NoteEdit: React.FC<NoteEditProps> = ({ mode }) => {
  const { id } = useParams<{ id: string }>();
  const [title, setTitle] = React.useState("");
  const [description, setDescription] = React.useState("");
  const [loading, setLoading] = React.useState(mode === "edit");
  const [error, setError] = React.useState<string | null>(null);
  const [saving, setSaving] = React.useState(false);
  const [deleting, setDeleting] = React.useState(false);
  const navigate = useNavigate();

  React.useEffect(() => {
    if (mode === "edit" && id) {
      fetch(`/api/notes/${id}`)
        .then((res) => {
          if (!res.ok) throw new Error(res.status === 404 ? "Note not found" : "Failed to load note");
          return res.json();
        })
        .then((data: Note) => {
          setTitle(data.title);
          setDescription(data.description || "");
          setLoading(false);
        })
        .catch((err) => {
          setError(err.message || "Failed to load note");
          setLoading(false);
        });
    }
  }, [mode, id]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    if (!title.trim()) {
      setError("Title is required");
      return;
    }

    setSaving(true);
    try {
      const payload = { title: title.trim(), description: description.trim() };
      const response = await fetch(mode === "create" ? "/api/notes" : `/api/notes/${id}`, {
        method: mode === "create" ? "POST" : "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        throw new Error(errorData?.detail || `Failed to ${mode} note`);
      }

      const data = await response.json();
      navigate(`/notes/${data.id}`);
    } catch (err) {
      setError((err as Error).message || `Failed to ${mode} note`);
      setSaving(false);
    }
  };

  const handleDelete = async () => {
    if (!id) return;
    setDeleting(true);
    try {
      const res = await fetch(`/api/notes/${id}`, { method: "DELETE" });
      if (!res.ok) throw new Error("Failed to delete note");
      toast.success("Note deleted");
      navigate("/notes");
    } catch (e) {
      toast.error("Failed to delete note");
    } finally {
      setDeleting(false);
    }
  };

  if (loading) return <div>Loading...</div>;

  return (
    <div className="max-w-2xl mx-auto w-full">
      <form onSubmit={handleSubmit} className="space-y-6">
        <h2 className="text-2xl font-bold mb-4">{mode === "create" ? "Create Note" : "Edit Note"}</h2>
        {error && <div className="text-red-500 mb-4">{error}</div>}
        <div>
          <label className="block mb-1 font-medium">Title</label>
          <Input
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            required
            maxLength={200}
            placeholder="Enter note title"
            disabled={saving}
          />
        </div>
        <div>
          <label className="block mb-1 font-medium">Description</label>
          <Textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            rows={6}
            placeholder="Enter note description (optional)"
            disabled={saving}
          />
        </div>
        <div className="flex gap-2 justify-end">
          <Button 
            type="button" 
            variant="outline" 
            onClick={() => navigate(mode === "edit" && id ? `/notes/${id}` : "/notes")}
            disabled={saving}
          >
            Cancel
          </Button>
          <Button type="submit" disabled={saving}>
            {saving ? "Saving..." : "Save"}
          </Button>
        </div>
      </form>
      {mode === "edit" && id && (
        <div className="mt-8 flex justify-end">
          <AlertDialog>
            <AlertDialogTrigger asChild>
              <Button variant="destructive">Delete</Button>
            </AlertDialogTrigger>
            <AlertDialogContent>
              <AlertDialogHeader>
                <AlertDialogTitle>Delete this note?</AlertDialogTitle>
                <AlertDialogDescription>
                  This action cannot be undone. Are you sure you want to delete this note?
                </AlertDialogDescription>
              </AlertDialogHeader>
              <AlertDialogFooter>
                <AlertDialogCancel>Cancel</AlertDialogCancel>
                <AlertDialogAction onClick={handleDelete} disabled={deleting}>
                  {deleting ? "Deleting..." : "Delete"}
                </AlertDialogAction>
              </AlertDialogFooter>
            </AlertDialogContent>
          </AlertDialog>
        </div>
      )}
    </div>
  );
};

export default NoteEdit; 