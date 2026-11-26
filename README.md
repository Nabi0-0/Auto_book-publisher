
# Automated Book Publishing Pipeline

A Python-based, human-in-the-loop pipeline for scraping chapter text, rewriting and reviewing it with an LLM, checking source fidelity, and storing approved versions.

The pipeline is designed to keep a human in control: generated content is reviewed before it is approved, and run artifacts are preserved for inspection.

## Features

- **Chapter scraping:** Uses Playwright to capture chapter text and a screenshot from supported webpages.
- **AI rewriting:** Rewrites source text in a configurable tone while aiming to preserve its events, characters, and relationships.
- **AI review:** Revises the draft against the original chapter, correcting issues and improving readability.
- **Source-fidelity check:** Flags potentially meaningful omissions, unsupported additions, or changes to the source. This is an advisory LLM check, not a guarantee of accuracy.
- **Human-in-the-loop review:** Approve, edit, request another rewrite, or cancel the pipeline.
- **Run artifacts:** Saves the source, writer draft, reviewed draft, fidelity result, screenshot, and approved chapter for each run.
- **Version storage:** Stores writer, reviewer, and final versions in ChromaDB.
- **Semantic retrieval with feedback:** Supports similarity search with reward-adjusted ranking.

## Project Structure

```text
Auto_book-publisher/
├── Scraping/
│   └── scraper.py
├── ai-pipeline/
│   ├── writer.py
│   ├── reviewer.py
│   ├── HITL_interface.py
│   └── llm_client.py
├── pipeline/
│   └── agentic_api.py
├── storage/
│   ├── chroma_config.py
│   ├── version_store.py
│   └── rl_search.py
├── tests/
├── outputs/
├── chroma_db/
├── .env.example
├── requirements.txt
└── README.md
```

## Requirements

- Python 3.10 or a compatible version supported by the project dependencies
- A Groq API key
- Playwright with Chromium installed

## Setup

Install the Python dependencies:

```powershell
pip install -r requirements.txt
```

Install the Playwright browser:

```powershell
playwright install chromium
```

Create a `.env.local` file in the project root using the following configuration:

```dotenv
# Groq API credentials
GROQ_API_KEY=your_groq_api_key_here

# LLM configuration
GROQ_MODEL=openai/gpt-oss-20b
GROQ_MAX_COMPLETION_TOKENS=2048
GROQ_REASONING_EFFORT=low

# Maximum additional writer generations per pipeline run
PIPELINE_MAX_REWRITES=3
```

Replace the placeholder with your own Groq API key. Keep `.env.local` private and never commit real credentials.

## Run the Pipeline

From the project root, run:

```powershell
python -m pipeline.agentic_api
```

Enter the chapter URL and a stable chapter ID when prompted.

Each run creates a unique directory under:

```text
outputs/runs/
```

The run directory preserves the generated artifacts, including the approved chapter when the pipeline completes.

## Human Review

After the writer and reviewer steps, the pipeline displays the fidelity-check result and asks for a human decision.

Available actions include:

- **Approve** the reviewed chapter
- **Edit** the draft
- **Request a rewrite**, subject to `PIPELINE_MAX_REWRITES`
- **Cancel** while preserving the run artifacts

The fidelity check is advisory. A `PASS` does not guarantee that the draft contains every source detail or that it is factually correct.

## Version Storage and Retrieval

Approved pipeline runs store the writer, reviewer, and final versions in ChromaDB with chapter and run metadata.

The retrieval module supports semantic search and adjusts ranking using stored feedback. This is a reward-adjusted retrieval heuristic; it is not a trained reinforcement-learning agent.

## Run Tests

Run the focused pipeline tests:

```powershell
python -m unittest tests.test_agentic_pipeline
```

Additional test modules cover the HITL interface, reviewer, scraper, version storage, and retrieval.

## Current Limitations

- The scraper currently extracts text using a MediaWiki-specific content selector. Other website layouts may require different extraction logic.
- The writer, reviewer, and fidelity checker send chapter text to the configured LLM. Long chapters may exceed model context or output limits.
- Fidelity checking relies on an LLM and may miss omissions or flag acceptable changes.
- The pipeline is interactive; a web UI and multi-chapter bulk publishing are not currently implemented.
- PDF/EPUB export is not currently implemented.

## Technology Stack

- Python
- Playwright
- Groq API through the OpenAI-compatible client
- ChromaDB
- Sentence Transformers

## Author

Ruru
