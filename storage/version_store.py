import os
import uuid
import chromadb
from sentence_transformers import SentenceTransformer

client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection(name="book_versions")

model = SentenceTransformer("all-MiniLM-L6-v2")
def store_version(chapter_id, version_tag, file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    embedding = model.encode(content).tolist()

    collection.add(
        ids=[str(uuid.uuid4())],
        documents=[content],
        metadatas=[{"chapter_id": chapter_id, "version": version_tag}],
        embeddings=[embedding]
    )
    print(f"Stored version: Chapter {chapter_id} - {version_tag}")

def persist_db():
    client.persist()
    print("ChromaDB changes persisted.")
