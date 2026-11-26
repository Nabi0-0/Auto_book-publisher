import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from storage import version_store


class TestStoreVersion(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)

        self.chapter_file = Path(self.temp_dir.name) / "chapter.txt"
        self.chapter_file.write_text("Chapter content", encoding="utf-8")

        self.collection = Mock()
        self.embedding_model = Mock()
        self.embedding_model.encode.return_value.tolist.return_value = [
            0.1,
            0.2,
            0.3,
        ]

        self.model_patch = patch.object(
            version_store, "get_embedding_model",
            return_value=self.embedding_model,
        )
        self.collection_patch = patch.object(
            version_store, "get_collection",
            return_value=self.collection,
        )

        self.model_patch.start()
        self.collection_patch.start()
        self.addCleanup(self.model_patch.stop)
        self.addCleanup(self.collection_patch.stop)

    def test_stores_run_id_in_metadata(self):
        version_id = version_store.store_version(
            chapter_id=" chapter-1 ",
            version_tag=" writer ",
            file_path=self.chapter_file,
            run_id=" run-123 ",
        )

        self.collection.add.assert_called_once_with(
            ids=[version_id],
            documents=["Chapter content"],
            metadatas=[
                {
                    "chapter_id": "chapter-1",
                    "version": "writer",
                    "run_id": "run-123",
                }
            ],
            embeddings=[[0.1, 0.2, 0.3]],
        )

    def test_omits_run_id_when_not_provided(self):
        version_id = version_store.store_version(
            chapter_id="chapter-1",
            version_tag="writer",
            file_path=self.chapter_file,
        )

        self.collection.add.assert_called_once_with(
            ids=[version_id],
            documents=["Chapter content"],
            metadatas=[
                {
                    "chapter_id": "chapter-1",
                    "version": "writer",
                }
            ],
            embeddings=[[0.1, 0.2, 0.3]],
        )


if __name__ == "__main__":
    unittest.main()