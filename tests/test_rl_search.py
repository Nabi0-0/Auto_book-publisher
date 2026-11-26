import unittest
from unittest.mock import MagicMock, patch

from storage.rl_search import RLContentRetriever


class TestRLContentRetriever(unittest.TestCase):
    def setUp(self):
        self.collection = MagicMock()
        self.client = MagicMock()
        self.client.get_or_create_collection.return_value = self.collection

        self.model = MagicMock()
        self.model.encode.return_value.tolist.return_value = [0.1, 0.2, 0.3]

        self.client_patcher = patch(
            "storage.rl_search.get_chroma_client",
            return_value=self.client,
        )
        self.model_patcher = patch(
            "storage.rl_search.SentenceTransformer",
            return_value=self.model,
        )

        self.client_patcher.start()
        self.model_patcher.start()
        self.addCleanup(self.client_patcher.stop)
        self.addCleanup(self.model_patcher.stop)

        self.retriever = RLContentRetriever()

    def test_store_with_reward_persists_reward_in_metadata(self):
        self.retriever.store_with_reward(
            "doc1",
            "Chapter text",
            {"chapter_id": "chapter-1"},
            2,
        )

        self.collection.add.assert_called_once_with(
            documents=["Chapter text"],
            ids=["doc1"],
            embeddings=[[0.1, 0.2, 0.3]],
            metadatas=[
                {"chapter_id": "chapter-1", "reward": 2.0}
            ],
        )

    def test_update_reward_persists_incremented_reward(self):
        self.collection.get.return_value = {
            "ids": ["doc1"],
            "metadatas": [{"chapter_id": "chapter-1", "reward": 2.0}],
        }

        self.retriever.update_reward("doc1", -0.5)

        self.collection.update.assert_called_once_with(
            ids=["doc1"],
            metadatas=[
                {"chapter_id": "chapter-1", "reward": 1.5}
            ],
        )

    def test_search_reranks_candidates_using_persisted_reward(self):
        self.collection.count.return_value = 2
        self.collection.query.return_value = {
            "documents": [["A", "B"]],
            "ids": [["a", "b"]],
            "metadatas": [[{"reward": 0.0}, {"reward": 5.0}]],
            "distances": [[0.1, 0.2]],
        }

        results = self.retriever.search("query", top_k=2)

        self.assertEqual(
            results,
            [("B", "b", 0.2), ("A", "a", 0.1)],
        )


if __name__ == "__main__":
    unittest.main()