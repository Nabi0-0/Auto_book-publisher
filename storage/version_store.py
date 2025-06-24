import os
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

CHROMA_DIR = "./chroma_db"
client = chromadb.Client(Settings(
    chroma_db_impl="duckdb+parquet",
    persist_directory=CHROMA_DIR
))

collection = client.get_or_create_collection(name="chapter_versions")
embedder = SentenceTransformer("all-MiniLM-L6-v2")
def load_text(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def store_version(chapter_id, version_tag, file_path):
    content = load_text(file_path)
    embedding = embedder.encode(content).tolist()
    doc_id = f"{chapter_id}_{version_tag}"
    collection.add(
        documents=[content],
        ids=[doc_id],
        metadatas=[{
            "chapter": chapter_id,
            "version": version_tag,
            "source_file": file_path
        }],
        embeddings=[embedding]
    )
    print(f"Stored: {doc_id} in ChromaDB")


def search_similar(text, top_k=3):
    embedding = embedder.encode(text).tolist()
    results = collection.query(query_embeddings=[embedding], n_results=top_k)
    return results


def get_all_versions(chapter_id):
    # Query for all versions of a chapter
    results = collection.get(where={"chapter": chapter_id})
    return results

def persist_db():
    client.persist()
