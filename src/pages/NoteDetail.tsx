import React from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { AlertDialog, AlertDialogTrigger, AlertDialogContent, AlertDialogHeader, AlertDialogTitle, AlertDialogDescription, AlertDialogFooter, AlertDialogCancel, AlertDialogAction } from "@/components/ui/alert-dialog";
import { toast } from "sonner";

interface Note {
  id: number;
  title: string;
  description?: string;
  created_at: string;
  updated_at?: string;
}

const NoteDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [note, setNote] = React.useState<Note | null>(null);
  const [loading, setLoading] = React.useState(true);
  const navigate = useNavigate();
  const [deleting, setDeleting] = React.useState(false);

  React.useEffect(() => {
    if (!id) return;
    fetch(`/api/notes/${id}`)
      .then((res) => {
        if (!res.ok) throw new Error("Not found");
        return res.json();
      })
      .then((data) => {
        setNote(data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, [id]);

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
  if (!note) return <div className="text-muted-foreground">Note not found.</div>;

  return (
    <div className="max-w-2xl mx-auto w-full">
      <div className="flex justify-between items-center mb-6">
        <Button variant="outline" onClick={() => navigate("/notes")}>Back</Button>
        <div className="flex gap-2">
          <Button onClick={() => navigate(`/notes/${note.id}/edit`)}>Edit</Button>
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
      </div>
      <Card className="w-full">
        <CardHeader>
          <CardTitle>{note.title}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="mb-4 whitespace-pre-line">{note.description || <span className="text-muted-foreground">No description.</span>}</div>
          <div className="text-xs text-muted-foreground">
            Created: {new Date(note.created_at).toLocaleString()}<br />
            {note.updated_at && (
              <>Updated: {new Date(note.updated_at).toLocaleString()}</>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default NoteDetail; 