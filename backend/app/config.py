import os
from pathlib import Path

# Get the user's home directory
HOME_DIR = Path.home()

# Create a dedicated directory for model cache
MODEL_CACHE_DIR = os.path.join(HOME_DIR, ".ai-local-intellect", "models")
os.makedirs(MODEL_CACHE_DIR, exist_ok=True)

# Database configuration
DATABASE_URL = os.path.join(os.path.dirname(__file__), "db", "posts.db")
DATABASE_URL = f"sqlite:///{DATABASE_URL}"

# Model configuration
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2" 