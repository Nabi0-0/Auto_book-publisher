📚 Automated Book Publication Pipeline
========================================
This project automates the workflow of scraping chapters from online sources, rewriting them using AI, reviewing the content, and enabling Human-In-The-Loop (HITL) edits before publishing. It includes versioning, search integration with ChromaDB, and can be controlled via CLI or web UI (optional).

____________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________

🔧 Features
 1. Web Scraping: Pull chapter content and screenshots from any user-provided URL using Playwright.
 2. AI Writer: Uses LLM (e.g., LLaMA/Gemini) to "spin" raw chapters into refined content.
 3. AI Reviewer: Automatically reviews and improves spun content.
 4. Human-in-the-Loop (HITL): Manual review/edit interface before finalizing.
 5. Version Control: Saves writer, reviewer, and final versions using ChromaDB.
 6. Reinforcement Learning (RL): Custom RL-based search mechanism (optional).
 7. Modular Agentic API: All steps executed via a single orchestrated pipeline.
    
______________________________________________________________________________________________________________________________________________

🗂️ Project Structure

  Auto_book_publisher/
  ├── Scraping/               # Web scraping logic
  │   └── scraper.py
  ├── ai-pipeline/            # AI writer, reviewer, HITL logic
  │   ├── writer.py
  │   ├── reviewer.py
  │   └── HITL_interface.py
  ├── storage/                # ChromaDB version store
  │   └── version_store.py
  ├── pipeline/
  │   └── agentic_api.py      # Main orchestrator
  ├── outputs/                # Auto-generated output files
  ├── .env
  └── README.md

______________________________________________________________________________________________________________________________________________

🚀 How to Run

Install Dependencies

  pip install -r requirements.txt
  playwright install

______________________________________________________________________________________________________________________________________________

🔁 Run the Full Pipeline (CLI)

  python cli.py --url "https://en.wikisource.org/wiki/The_Gates_of_Morning/Book_1/Chapter_1" --chapter 1 (example url used)
  Or you can run and provide input interactively: python cli.py

______________________________________________________________________________________________________________________________________________

🧠 Tech Stack
  Python 3.10+
  Playwright - Web scraping & screenshotting
  LLMs - AI writing and reviewing (LLaMA/Gemini/etc.)
  ChromaDB - For version control and search
  Reinforcement Learning - RL-based document retrieval (optional)

______________________________________________________________________________________________________________________________________________

✅ TODO / Coming Soon
 Web UI Improvements
 Multi-chapter bulk publishing
 Advanced RL-based retrieval agent
 PDF/EPUB export
______________________________________________________________________________________________________________________________________________

👤 Built By
Ruru | Making publishing smarter with AI 💡

