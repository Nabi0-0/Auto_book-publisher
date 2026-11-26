import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env.local")

for directory in ("Scraping", "ai-pipeline", "storage"):
    sys.path.insert(0, str(PROJECT_ROOT / directory))

from writer import spin_text_with_llama
from reviewer import review_text_with_llama, check_source_fidelity
from HITL_interface import get_human_decision
from version_store import store_version
from scraper import scrape_chapter


OUTPUT_DIR = PROJECT_ROOT / "outputs"
RUNS_DIR = OUTPUT_DIR / "runs"


def get_max_rewrites() -> int:
    raw_value = os.getenv("PIPELINE_MAX_REWRITES", "3")

    try:
        max_rewrites = int(raw_value)
    except ValueError as exc:
        raise ValueError(
            "PIPELINE_MAX_REWRITES must be an integer."
        ) from exc

    if max_rewrites < 0:
        raise ValueError(
            "PIPELINE_MAX_REWRITES cannot be negative."
        )

    return max_rewrites


def create_run_directory() -> Path:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_id = f"{timestamp}-{uuid.uuid4().hex[:8]}"

    run_directory = RUNS_DIR / run_id
    run_directory.mkdir(parents=True, exist_ok=False)

    return run_directory


def save_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def run_pipeline() -> None:
    chapter_url = input("Enter the chapter URL: ").strip()

    if not chapter_url:
        raise ValueError("Chapter URL cannot be empty.")

    chapter_id = input("Enter a stable chapter ID: ").strip()

    if not chapter_id:
        raise ValueError("Chapter ID cannot be empty.")

    max_rewrites = get_max_rewrites()
    run_directory = create_run_directory()
    run_id = run_directory.name

    raw_path = run_directory / "raw.txt"
    spun_path = run_directory / "writer.txt"
    reviewed_path = run_directory / "reviewed.txt"
    fidelity_path = run_directory / "fidelity.txt"
    final_path = run_directory / "final.txt"
    screenshot_path = run_directory / "screenshot.png"

    print(f"\nPipeline run directory: {run_directory}")

    scrape_chapter(
        chapter_url,
        str(screenshot_path),
        str(raw_path),
    )

    if not raw_path.is_file():
        raise FileNotFoundError(
            "Scraping did not produce a raw chapter."
        )

    raw_text = raw_path.read_text(encoding="utf-8")

    if not raw_text.strip():
        raise ValueError("The scraped chapter is empty.")

    spun_text = spin_text_with_llama(raw_text)
    save_text(spun_path, spun_text)

    rewrite_count = 0

    while True:
        reviewed_text = review_text_with_llama(raw_text, spun_text)
        save_text(reviewed_path, reviewed_text)

        fidelity_result = check_source_fidelity(raw_text, reviewed_text)
        save_text(fidelity_path, fidelity_result)

        if fidelity_result.upper().startswith("FLAG"):
            print("\nFidelity warning:")
            print(fidelity_result)
        else:
            print("\nFidelity check: PASS")

        decision, decision_content = get_human_decision(
            reviewed_text,
            allow_rewrite=rewrite_count < max_rewrites,
        )

        if decision == "approve":
            final_text = decision_content
            break

        if decision == "edit":
            spun_text = decision_content
            continue

        if decision == "rewrite":
            if rewrite_count >= max_rewrites:
                print(
                    f"Maximum rewrite limit ({max_rewrites}) reached. "
                    "Please approve, edit, or cancel."
                )
                continue

            rewrite_count += 1
            print(
                f"Starting rewrite {rewrite_count} of {max_rewrites}."
            )

            spun_text = spin_text_with_llama(raw_text)
            save_text(spun_path, spun_text)
            continue

        if decision == "cancel":
            print(
                "\nPipeline cancelled. Run artifacts preserved at: "
                f"{run_directory}"
            )
            return

        raise RuntimeError(f"Unexpected HITL decision: {decision}")

    save_text(final_path, final_text)

    store_version(
        chapter_id, "writer", str(spun_path), run_id=run_id
    )
    store_version(
        chapter_id, "reviewer", str(reviewed_path), run_id=run_id
    )
    store_version(
        chapter_id, "final", str(final_path), run_id=run_id
    )

    print(f"\nPipeline complete. Approved chapter: {final_path}")


if __name__ == "__main__":
    run_pipeline()