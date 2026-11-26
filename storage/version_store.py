
import uuid
from functools import lru_cache
from pathlib import Path

from sentence_transformers import SentenceTransformer

from storage.chroma_config import (
    BOOK_VERSIONS_COLLECTION,
    EMBEDDING_MODEL_NAME,
    get_chroma_client,
)


@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    return SentenceTransformer(EMBEDDING_MODEL_NAME)


@lru_cache(maxsize=1)
def get_collection():
    client = get_chroma_client()
    return client.get_or_create_collection(
        name=BOOK_VERSIONS_COLLECTION
    )


def store_version(
    chapter_id: str,
    version_tag: str,
    file_path: str | Path,
    run_id: str | None = None,
) -> str:
    if not chapter_id or not chapter_id.strip():
        raise ValueError("Chapter ID cannot be empty.")

    if not version_tag or not version_tag.strip():
        raise ValueError("Version tag cannot be empty.")

    path = Path(file_path)

    if not path.is_file():
        raise FileNotFoundError(f"Version file not found: {path}")

    content = path.read_text(encoding="utf-8")

    if not content.strip():
        raise ValueError("Version content cannot be empty.")

    embedding = get_embedding_model().encode(content).tolist()
    collection = get_collection()

    version_id = str(uuid.uuid4())

    collection.add(
        ids=[version_id],
        documents=[content],
        metadatas=[
            {
                "chapter_id": chapter_id.strip(),
                "version": version_tag.strip(),
                **({"run_id": run_id.strip()} if run_id and run_id.strip() else {}),
            }
        ],
        embeddings=[embedding],
    )

    print(
        f"Stored version: Chapter {chapter_id} - {version_tag}"
    )

    return version_id
