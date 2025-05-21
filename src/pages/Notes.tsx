import React from "react";
import { useNavigate } from "react-router-dom";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { X } from "lucide-react";
import { AlertDialog, AlertDialogTrigger, AlertDialogContent, AlertDialogHeader, AlertDialogTitle, AlertDialogDescription, AlertDialogFooter, AlertDialogCancel, AlertDialogAction } from "@/components/ui/alert-dialog";
import { toast } from "sonner";

interface Note {
  id: number;
  title: string;
  description?: string;
  created_at: string;
  updated_at?: string;
}

interface NotesResponse {
  status: string;
  data: Note[];
}

const Notes: React.FC = () => {
  const [notes, setNotes] = React.useState<Note[]>([]);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);
  const navigate = useNavigate();
  const [deletingId, setDeletingId] = React.useState<number | null>(null);

  React.useEffect(() => {
    fetch("/api/notes")
      .then((res) => {
        if (!res.ok) {
          throw new Error(`HTTP error! status: ${res.status}`);
        }
        return res.json();
      })
      .then((response: NotesResponse) => {
        setNotes(response.data || []);
        setLoading(false);
      })
      .catch((error) => {
        console.error("Error fetching notes:", error);
        setError("Failed to load notes");
        setLoading(false);
      });
  }, []);

  const handleDelete = async (id: number) => {
    setDeletingId(id);
    try {
      const res = await fetch(`/api/notes/${id}`, { method: "DELETE" });
      if (!res.ok) throw new Error("Failed to delete note");
      setNotes((prev) => prev.filter((n) => n.id !== id));
      toast.success("Note deleted");
    } catch (e) {
      toast.error("Failed to delete note");
    } finally {
      setDeletingId(null);
    }
  };

  return (
    <div className="max-w-2xl mx-auto w-full">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold">Notes</h2>
        <Button onClick={() => navigate("/notes/new")}>Create Note</Button>
      </div>
      {loading ? (
        <div>Loading...</div>
      ) : error ? (
        <div className="text-red-500">{error}</div>
      ) : notes.length === 0 ? (
        <div className="text-muted-foreground">No notes found.</div>
      ) : (
        <div className="flex flex-col gap-4">
          {notes.map((note) => (
            <div key={note.id} className="relative">
              <Card
                className="w-full cursor-pointer hover:shadow-lg"
                onClick={() => navigate(`/notes/${note.id}`)}
              >
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle>{note.title}</CardTitle>
                    <AlertDialog>
                      <AlertDialogTrigger asChild>
                        <Button
                          type="button"
                          size="icon"
                          variant="ghost"
                          className="ml-2 text-muted-foreground hover:text-red-500"
                          onClick={(e) => { e.stopPropagation(); }}
                          aria-label="Delete note"
                        >
                          <X className="w-4 h-4" />
                        </Button>
                      </AlertDialogTrigger>
                      <AlertDialogContent onClick={e => e.stopPropagation()}>
                        <AlertDialogHeader>
                          <AlertDialogTitle>Delete this note?</AlertDialogTitle>
                          <AlertDialogDescription>
                            This action cannot be undone. Are you sure you want to delete this note?
                          </AlertDialogDescription>
                        </AlertDialogHeader>
                        <AlertDialogFooter>
                          <AlertDialogCancel>Cancel</AlertDialogCancel>
                          <AlertDialogAction
                            onClick={() => handleDelete(note.id)}
                            disabled={deletingId === note.id}
                          >
                            {deletingId === note.id ? "Deleting..." : "Delete"}
                          </AlertDialogAction>
                        </AlertDialogFooter>
                      </AlertDialogContent>
                    </AlertDialog>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="text-xs text-muted-foreground">
                    Created: {new Date(note.created_at).toLocaleString()}
                  </div>
                </CardContent>
              </Card>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Notes; 