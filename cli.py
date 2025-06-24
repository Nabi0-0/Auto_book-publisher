import os
import sys
import argparse

# Add module paths
sys.path.append("Scraping")
sys.path.append("ai-pipeline")
sys.path.append("storage")

from writer import spin_text_with_llama
from dotenv import load_dotenv
from reviewer import review_text_with_llama
from HITL_interface import load_text, save_text, manual_edit
from version_store import store_version, persist_db

def check_file_exists(path):
    if not os.path.exists(path):
        print(f"Required file not found: {path}")
        return False
    return True

def run_pipeline(raw_path="outputs/raw_chapter1.txt", 
                 spun_path="outputs/chapter1_spun_v1.txt", 
                 reviewed_path="outputs/chapter1_reviewed_v1.txt", 
                 final_path="outputs/chapter1_final_v1.txt", 
                 chapter_id="1"):

    print("\n Starting Agentic Book Pipeline...")
    print("Loading raw chapter...")
    if not check_file_exists(raw_path):
        return
    raw_text = load_text(raw_path)
    print("Spinning chapter with AI Writer...")
    spun_text = spin_text_with_llama(raw_text)
    save_text(spun_path, spun_text)
    print(f"Spun version saved to: {spun_path}")
    print("Reviewing spun text with AI Reviewer...")
    reviewed_text = review_text_with_llama(spun_text)
    save_text(reviewed_path, reviewed_text)
    print(f"Reviewed version saved to: {reviewed_path}")
    print("Launching HITL interface for approval or edits...")
    from HITL_interface import main as HITL_main
    HITL_main()

    # Step 5: Finalization check
    if os.path.exists(final_path):
        print(f"\n Pipeline complete. Final approved file: {final_path}")
    else:
        print("\n Pipeline ended without final approval. Check HITL edits or retry.")

    #print(" Storing all versioned outputs...")
    store_version(chapter_id=chapter_id, version_tag="writer", file_path=spun_path)
    if os.path.exists(reviewed_path):
        store_version(chapter_id=chapter_id, version_tag="reviewer", file_path=reviewed_path)
    if os.path.exists(final_path):
        store_version(chapter_id=chapter_id, version_tag="final", file_path=final_path)

    persist_db()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Agentic Book Pipeline CLI")
    parser.add_argument("--raw", default="outputs/raw_chapter1.txt", help="Path to raw chapter file")
    parser.add_argument("--spun", default="outputs/chapter1_spun_v1.txt", help="Path to save spun chapter")
    parser.add_argument("--reviewed", default="outputs/chapter1_reviewed_v1.txt", help="Path to save reviewed chapter")
    parser.add_argument("--final", default="outputs/chapter1_final_v1.txt", help="Path to save final approved chapter")
    parser.add_argument("--chapter", default="1", help="Chapter ID")

    args = parser.parse_args()
    run_pipeline(raw_path=args.raw, spun_path=args.spun, reviewed_path=args.reviewed, final_path=args.final, chapter_id=args.chapter)