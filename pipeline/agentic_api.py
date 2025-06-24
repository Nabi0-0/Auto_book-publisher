import os
import sys
sys.path.append("Scraping")
sys.path.append("ai-pipeline")
sys.path.append("storage")

from writer import spin_text_with_llama
from dotenv import load_dotenv
from reviewer import review_text_with_llama
from HITL_interface import load_text, save_text, manual_edit
from version_store import store_version, persist_db

RAW_PATH = "outputs/raw_chapter1.txt"
SPUN_PATH = "outputs/chapter1_spun_v1.txt"
REVIEWED_PATH = "outputs/chapter1_reviewed_v1.txt"
FINAL_PATH = "outputs/chapter1_final_v1.txt"

def check_file_exists(path):
    if not os.path.exists(path):
        print(f"Required file not found: {path}")
        return False
    return True

def run_pipeline():
    print("\n Starting Agentic Book Pipeline...")
    print("Loading raw chapter...")
    if not check_file_exists(RAW_PATH):
        return
    raw_text = load_text(RAW_PATH)
    spun_text = spin_text_with_llama(raw_text)
    save_text(SPUN_PATH, spun_text)
    print(f"Spun version saved to: {SPUN_PATH}")

    reviewed_text = review_text_with_llama(spun_text)
    save_text(REVIEWED_PATH, reviewed_text)
    print(f"Reviewed version saved to: {REVIEWED_PATH}")
    from HITL_interface import main as HITL_main
    HITL_main()

    if os.path.exists(FINAL_PATH):
        print(f"\n Pipeline complete. Final approved file: {FINAL_PATH}")
    else:
        print("\n Pipeline ended without approval. Check HITL edits or retry.")
    
    store_version(chapter_id="1", version_tag="writer", file_path=SPUN_PATH)
    store_version(chapter_id="1", version_tag="reviewer", file_path=REVIEWED_PATH)
    store_version(chapter_id="1", version_tag="final", file_path=FINAL_PATH)

    persist_db()

if __name__ == "__main__":
    run_pipeline()
