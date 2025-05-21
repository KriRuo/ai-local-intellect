import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'posts.db')

def main():
    print(f"Checking database: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    try:
        # List all tables
        cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cur.fetchall()]
        print(f"Tables in DB: {tables}")
        if 'notes' not in tables:
            print("Table 'notes' does NOT exist!")
            return
        # Print schema
        cur.execute("PRAGMA table_info(notes);")
        schema = cur.fetchall()
        print("Schema for 'notes':")
        for col in schema:
            print(col)
        # Count rows
        cur.execute("SELECT COUNT(*) FROM notes;")
        count = cur.fetchone()[0]
        print(f"Rows in 'notes': {count}")
        # Try inserting a test note
        try:
            cur.execute("INSERT INTO notes (title, description) VALUES (?, ?)", ("Test Note", "This is a test note."))
            conn.commit()
            print("Successfully inserted a test note.")
        except Exception as e:
            print(f"Error inserting note: {e}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    main() 