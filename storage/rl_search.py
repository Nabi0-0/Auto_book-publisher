from math import isfinite

from sentence_transformers import SentenceTransformer

from storage.chroma_config import (
    CHAPTERS_COLLECTION,
    EMBEDDING_MODEL_NAME,
    get_chroma_client,
)


class RLContentRetriever:
    def __init__(
        self,
        collection_name=CHAPTERS_COLLECTION,
        model_name=EMBEDDING_MODEL_NAME,
    ):
        self.client = get_chroma_client()
        self.collection = self.client.get_or_create_collection(
            name=collection_name
        )
        self.embedding_model = SentenceTransformer(model_name)

    def _embed(self, text):
        return self.embedding_model.encode(text).tolist()

    def store_with_reward(self, id, text, metadata, reward):
        if not isinstance(reward, (int, float)) or not isfinite(reward):
            raise ValueError("reward must be a finite number")

        stored_metadata = dict(metadata)
        stored_metadata["reward"] = float(reward)

        embedding = self._embed(text)

        self.collection.add(
            documents=[text],
            ids=[id],
            embeddings=[embedding],
            metadatas=[stored_metadata],
        )

    def search(self, query, top_k=5):
        if not isinstance(top_k, int) or top_k < 1:
            raise ValueError("top_k must be at least 1")

        collection_count = self.collection.count()

        if collection_count == 0:
            return []

        query_embedding = self._embed(query)

        # Retrieve candidates, then rerank them using persisted feedback.
        candidate_count = min(top_k * 5, collection_count)
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=candidate_count,
            include=["documents", "metadatas", "distances"],
        )

        candidates = []
        for document, doc_id, metadata, distance in zip(
            results["documents"][0],
            results["ids"][0],
            results["metadatas"][0],
            results["distances"][0],
        ):
            reward = float((metadata or {}).get("reward", 0.0))
            adjusted_score = distance - (0.1 * reward)
            candidates.append(
                (document, doc_id, distance, adjusted_score)
            )

        candidates.sort(key=lambda item: item[3])

        return [
            (document, doc_id, distance)
            for document, doc_id, distance, _ in candidates[:top_k]
        ]

    def update_reward(self, doc_id, feedback):
        if not isinstance(feedback, (int, float)) or not isfinite(feedback):
            raise ValueError("feedback must be a finite number")

        result = self.collection.get(
            ids=[doc_id],
            include=["metadatas"],
        )

        if not result["ids"]:
            raise ValueError(f"Document not found: {doc_id}")

        metadata = dict(result["metadatas"][0] or {})
        current_reward = float(metadata.get("reward", 0.0))
        updated_reward = current_reward + float(feedback)
        metadata["reward"] = updated_reward

        self.collection.update(
            ids=[doc_id],
            metadatas=[metadata],
        )

        print(f"Updated reward for {doc_id}: {updated_reward}")