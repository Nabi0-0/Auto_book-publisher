
from pathlib import Path

import chromadb
from chromadb.config import Settings


PROJECT_ROOT = Path(__file__).resolve().parent.parent

CHROMA_DB_PATH = PROJECT_ROOT / "chroma_db"

BOOK_VERSIONS_COLLECTION = "book_versions"
CHAPTERS_COLLECTION = "chapters"

EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"


def get_chroma_client():
    return chromadb.PersistentClient(
        path=str(CHROMA_DB_PATH),
        settings=Settings(anonymized_telemetry=False),
    )
