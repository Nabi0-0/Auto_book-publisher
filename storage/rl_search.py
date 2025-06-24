import numpy as np
import random
from sentence_transformers import SentenceTransformer, util
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions

class RLContentRetriever:
    def __init__(self, collection_name="chapters", model_name="all-MiniLM-L6-v2"):
        self.client = chromadb.Client(Settings(persist_directory="storage/chroma_db", anonymized_telemetry=False))
        self.collection = self.client.get_or_create_collection(name=collection_name)
        self.embedding_model = SentenceTransformer(model_name)
        self.rewards = {}  # key: id, value: reward score

    def _embed(self, text):
        return self.embedding_model.encode(text, convert_to_tensor=True).tolist()

    def store_with_reward(self, id, text, metadata, reward):
        embedding = self._embed(text)
        self.rewards[id] = reward
        self.collection.add(documents=[text], ids=[id], embeddings=[embedding], metadatas=[metadata])

    def search(self, query, top_k=5):
        query_embedding = self._embed(query)
        results = self.collection.query(query_embeddings=[query_embedding], n_results=top_k)

        docs = results["documents"][0]
        ids = results["ids"][0]
        scores = results["distances"][0]  # cosine similarity
        epsilon = 0.2
        scored_results = []
        for doc, doc_id, sim_score in zip(docs, ids, scores):
            reward = self.rewards.get(doc_id, 0)
            final_score = (1 - epsilon) * sim_score + epsilon * reward
            scored_results.append((doc, doc_id, final_score))
        ranked = sorted(scored_results, key=lambda x: x[2], reverse=True)
        return ranked[:top_k]

    def update_reward(self, doc_id, feedback):
        # +1 for good feedback, -1 for bad
        self.rewards[doc_id] = self.rewards.get(doc_id, 0) + feedback
        print(f"Updated reward for {doc_id}: {self.rewards[doc_id]}")


# Example Usage:
# retriever = RLContentRetriever()
# retriever.store_with_reward("ch1-v1", text, {"tag": "writer"}, reward=1)
# results = retriever.search("hero fights dragon")
# retriever.update_reward("ch1-v1", feedback=1)
