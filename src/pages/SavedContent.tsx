import { useEffect, useState } from "react";

type Post = {
  id: number;
  title: string;
  content: string;
  // ...other fields as needed
};

type SavedPost = {
  id: number;
  post_id: number;
  saved_at: string;
  post: Post;
};

export default function SavedContent() {
  const [saved, setSaved] = useState<SavedPost[]>([]);
  const [loading, setLoading] = useState(true);
  const [deleting, setDeleting] = useState<number | null>(null);

  useEffect(() => {
    fetch("/api/saved")
      .then((res) => res.json())
      .then(setSaved)
      .finally(() => setLoading(false));
  }, []);

  const handleDelete = async (post_id: number) => {
    setDeleting(post_id);
    await fetch(`/api/saved/${post_id}`, { method: "DELETE" });
    setSaved((prev) => prev.filter((item) => item.post_id !== post_id));
    setDeleting(null);
    // Optionally show a toast here
  };

  if (loading) return <div className="p-4">Loading...</div>;

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">Saved Content</h1>
      {saved.length === 0 ? (
        <div>No saved posts yet.</div>
      ) : (
        <div className="grid gap-4">
          {saved.map((item) => (
            <div key={item.id} className="border p-4 rounded bg-white shadow relative">
              <h2 className="text-xl font-semibold">{item.post.title}</h2>
              <p className="text-gray-700">{item.post.content}</p>
              <button
                className="absolute top-2 right-2 text-red-500 hover:text-red-700"
                onClick={() => handleDelete(item.post_id)}
                disabled={deleting === item.post_id}
                title="Remove from saved"
                aria-label="Remove from saved"
              >
                {/* Trash icon (Heroicons outline) */}
                <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none"
                  viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                    d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
