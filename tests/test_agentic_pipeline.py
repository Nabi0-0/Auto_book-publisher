import tempfile
import unittest
from pathlib import Path
from unittest.mock import call, patch

import pipeline.agentic_api as pipeline
from contextlib import redirect_stdout
from io import StringIO


class TestPipelineOrchestration(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)

        root = Path(self.temp_dir.name)
        self.output_dir = root / "outputs"
        self.runs_dir = self.output_dir / "runs"

        self.patch_runs = patch.object(
            pipeline, "RUNS_DIR", self.runs_dir
        )
        self.patch_runs.start()
        self.addCleanup(self.patch_runs.stop)

    def get_run_directory(self):
        run_directories = list(self.runs_dir.iterdir())
        self.assertEqual(len(run_directories), 1)
        return run_directories[0]

    def run_with_mocks(
    self,
    decisions,
    writer_outputs,
    reviewer_outputs,
    fidelity_result="PASS",
):

        def fake_scrape(url, screenshot_path, text_path):
            path = Path(text_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("Original chapter", encoding="utf-8")

        with (
            patch.object(
                pipeline, "scrape_chapter", side_effect=fake_scrape
            ) as scrape,
            patch.object(
                pipeline,
                "spin_text_with_llama",
                side_effect=writer_outputs,
            ) as writer,
            patch.object(
                pipeline,
                "review_text_with_llama",
                side_effect=reviewer_outputs,
            ) as reviewer,
            patch.object(
                pipeline,
                "get_human_decision",
                side_effect=decisions,
            ) as decision,
            patch.object(pipeline, "store_version") as store,
            patch(
                "builtins.input",
                side_effect=[
                    "https://example.com/chapter",
                    "test_chapter",
                ],
            ),
            patch.object(
                pipeline,
                "check_source_fidelity",
                return_value=fidelity_result,
            ) as fidelity,
        ):
            pipeline.run_pipeline()

        return scrape, writer, reviewer, decision, store, fidelity

    def test_approval_saves_final_and_stores_versions(self):
        self.run_with_mocks(
            [("approve", "Approved chapter")],
            ["Writer draft"],
            ["Reviewed chapter"],
        )

        run_dir = self.get_run_directory()

        self.assertEqual(
            (run_dir / "final.txt").read_text(encoding="utf-8"),
            "Approved chapter",
        )
        self.assertTrue((run_dir / "raw.txt").is_file())
        self.assertTrue((run_dir / "writer.txt").is_file())
        self.assertTrue((run_dir / "reviewed.txt").is_file())

    def test_manual_edit_returns_to_reviewer(self):
        _, _, reviewer, _, store, _ = self.run_with_mocks(
            [
                ("edit", "Human-edited draft"),
                ("approve", "Approved edited chapter"),
            ],
            ["Writer draft"],
            ["First review", "Second review"],
        )

        run_dir = self.get_run_directory()

        self.assertEqual(
            [args.args for args in reviewer.call_args_list],
            [
                ("Original chapter", "Writer draft"),
                ("Original chapter", "Human-edited draft"),
            ],
        )
        self.assertEqual(
            (run_dir / "final.txt").read_text(encoding="utf-8"),
            "Approved edited chapter",
        )
        self.assertEqual(store.call_count, 3)

    def test_rewrite_regenerates_from_original_source(self):
        _, writer, _, _, store, _ = self.run_with_mocks(
            [
                ("rewrite", "First reviewed chapter"),
                ("approve", "Approved rewritten chapter"),
            ],
            ["First writer draft", "Second writer draft"],
            ["First review", "Second review"],
        )

        run_dir = self.get_run_directory()

        self.assertEqual(
            writer.call_args_list,
            [
                call("Original chapter"),
                call("Original chapter"),
            ],
        )
        self.assertEqual(
            (run_dir / "final.txt").read_text(encoding="utf-8"),
            "Approved rewritten chapter",
        )
        self.assertEqual(store.call_count, 3)

    def test_cancellation_preserves_run_without_final(self):
        self.output_dir.mkdir(parents=True, exist_ok=True)

        old_final = self.output_dir / "chapter1_final_v1.txt"
        old_final.write_text(
            "Previous approved chapter",
            encoding="utf-8",
        )

        _, _, _, _, store, _ = self.run_with_mocks(
            [("cancel", "Reviewed chapter")],
            ["Writer draft"],
            ["Reviewed chapter"],
        )

        run_dir = self.get_run_directory()

        self.assertFalse((run_dir / "final.txt").exists())
        self.assertEqual(
            old_final.read_text(encoding="utf-8"),
            "Previous approved chapter",
        )
        store.assert_not_called()

    def test_rewrite_limit_is_enforced(self):
        with patch.object(pipeline, "get_max_rewrites", return_value=1):
            _, writer, _, _, store, _ = self.run_with_mocks(
                decisions=[
                    ("rewrite", "First review"),
                    ("rewrite", "Second review"),
                    ("approve", "Approved chapter"),
                ],
                writer_outputs=[
                    "Initial draft",
                    "Rewritten draft",
                ],
                reviewer_outputs=[
                    "First review",
                    "Second review",
                    "Final review",
                ],
            )

        self.assertEqual(writer.call_count, 2)
        self.assertEqual(store.call_count, 3)

    def test_zero_rewrites_still_allows_approval(self):
        with patch.object(pipeline, "get_max_rewrites", return_value=0):
            _, writer, _, _, store, _ = self.run_with_mocks(
                decisions=[
                    ("rewrite", "First review"),
                    ("approve", "Approved chapter"),
                ],
                writer_outputs=["Initial draft"],
                reviewer_outputs=["First review", "Final review"],
            )

        self.assertEqual(writer.call_count, 1)
        self.assertEqual(store.call_count, 3)

    def test_invalid_rewrite_limit_rejected(self):
        with patch.dict(
            "os.environ",
            {"PIPELINE_MAX_REWRITES": "abc"},
        ):
            with self.assertRaisesRegex(
                ValueError,
                "must be an integer",
            ):
                pipeline.get_max_rewrites()

    def test_negative_rewrite_limit_rejected(self):
        with patch.dict(
            "os.environ",
            {"PIPELINE_MAX_REWRITES": "-1"},
        ):
            with self.assertRaisesRegex(
                ValueError,
                "cannot be negative",
            ):
                pipeline.get_max_rewrites()

    def test_default_rewrite_limit_is_three(self):
        with patch.dict("os.environ", {}, clear=True):
            self.assertEqual(pipeline.get_max_rewrites(), 3)

    def test_blank_chapter_id_rejected_before_run_creation(self):
        with (
            patch(
                "builtins.input",
                side_effect=[
                    "https://example.com/chapter",
                    "   ",
                ],
            ),
            self.assertRaisesRegex(
                ValueError,
                "Chapter ID cannot be empty",
            ),
        ):
            pipeline.run_pipeline()

        self.assertFalse(self.runs_dir.exists())
        
    def test_fidelity_flag_is_displayed_as_warning(self):
        output = StringIO()

        with redirect_stdout(output):
            self.run_with_mocks(
                decisions=[("approve", "Approved chapter")],
                writer_outputs=["Writer draft"],
                reviewer_outputs=["Reviewed chapter"],
                fidelity_result="FLAG: Important source details are missing.",
            )

        displayed = output.getvalue()

        self.assertIn("Fidelity warning:", displayed)
        self.assertIn("FLAG: Important source details are missing.", displayed)
        self.assertLess(
            displayed.index("Fidelity warning:"),
            displayed.index("Pipeline complete."),
        )


if __name__ == "__main__":
    unittest.main()