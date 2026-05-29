# Antriksha Vimanshastra — NASA Handbook RAG QA System

A Retrieval-Augmented Generation (RAG) system built to answer complex technical questions over large, structured PDF documents. The primary target document is the **NASA Systems Engineering Handbook (SP-2016-6105 Rev2)** — a 270-page technical reference with process diagrams, decision trees, multi-page tables, and heavy cross-chapter referencing.

---

## Problem Statement

Most RAG implementations work well on simple, self-contained documents where each chunk is independently meaningful and keyword similarity finds the right passage. Technical manuals break this assumption:

- Information in one chapter references concepts defined in another
- Tables span multiple pages
- Diagrams contain critical decision logic that plain text extraction misses
- A figure caption on page 87 only makes sense with the process description on page 42

This system is built to handle those structural challenges.

---

## Features

### Core (MVP)
- Full PDF ingestion with a searchable knowledge base built on Weaviate Cloud
- Natural language Q&A with source citations (page number, section, title)
- Section-boundary-aware chunking — no arbitrary token window cuts
- Basic cross-reference resolution: if an answer spans two sections, both are retrieved
- Hybrid search (vector + keyword) with Cohere reranking

### Stretch Goals (Implemented / In Progress)
- **Hierarchical chunking**: parent-child section relationships are preserved in chunk metadata (`path`, `section`, `title`)
- **Cross-reference extraction**: regex-based detection of `Section X.Y`, `Chapter N`, `Appendix Z` references stored per chunk
- **Image extraction**: images are extracted from the PDF with base64 encoding (visual description integration is a planned enhancement)
- **Acronym density**: the LLM is prompted to resolve and expand acronyms found in chunks before answering

---

## Architecture

```
PDF Document (NASA SE Handbook)
        │
        ▼
┌──────────────────────────────┐
│  chunking/chunk.py           │
│  • extract_pdf_elements()    │  ← PyMuPDF: text blocks + images
│  • build_document_tree()     │  ← hierarchical section tree
│  • extract_references()      │  ← cross-reference detection
│  • split_chunks()            │  ← 500-char chunks, 100-char overlap
└──────────────┬───────────────┘
               │ chunks.jsonl
               ▼
┌──────────────────────────────┐
│  ingestion/ingest.py         │
│  • batch ingest to Weaviate  │  ← batch size 100
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│  Weaviate Cloud              │
│  Collection: NasaHandbook    │
│  Vector: MasterVector        │  ← Snowflake arctic-embed-l-v2.0
│  Reranker: Cohere            │
└──────────────┬───────────────┘
               │
    ┌──────────┴──────────┐
    │  Query time         │
    ▼                     ▼
┌───────────────┐  ┌──────────────────────────┐
│  retriever/   │  │  ChatModel/              │
│  hybrid search│→ │  answergenerator()       │
│  + reranking  │  │  ChatGroq (gpt-oss-120b) │
│  top-10 chunks│  │  citation-aware prompt   │
└───────────────┘  └──────────────────────────┘
                            │
                            ▼
                   Answer + source citations
                   (page, section, title)
```

---

## Repository Structure

```
.
├── app.py                       # Streamlit web interface
├── main.py                      # CLI entry point
├── chunking/
│   └── chunk.py                 # PDF parsing, tree building, chunking pipeline
├── ingestion/
│   └── ingest.py                # Batch ingest chunks into Weaviate
├── embeddinggeneration/
│   └── generate.py              # Sentence Transformer embedding utilities
├── retriever/
│   └── retrievechunks.py        # Hybrid search + Cohere reranking
├── vectorstore/
│   ├── vectordb.py              # Weaviate Cloud connection
│   ├── collection.py            # "NasaHandbook" schema definition
│   └── cleanup.py               # Collection deletion utility
├── ChatModel/
│   ├── model.py                 # ChatGroq model initialization
│   ├── prompt.py                # Citation-aware prompt template
│   └── bot.py                   # Answer generation orchestration
├── pyproject.toml
├── requirements.txt
└── uv.lock
```

---

## Setup

### Prerequisites

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) (recommended) or pip
- A [Weaviate Cloud](https://console.weaviate.cloud/) instance with the `NasaHandbook` collection created
- A [Groq](https://console.groq.com/) API key
- A [Cohere](https://cohere.com/) API key (for reranking)

### Install Dependencies

```bash
# Using uv (recommended)
uv sync

# Or using pip
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file in the project root:

```env
WEAVIATE_URL=https://<your-cluster>.weaviate.network
WEAVIATE_API_KEY=<your-weaviate-api-key>
COHERE_API_KEY=<your-cohere-api-key>
GROQ_API_KEY=<your-groq-api-key>
```

---

## Usage

### 1. Ingest the Document

Download the NASA SE Handbook PDF and run the chunking pipeline:

```python
# In main.py, uncomment and run:
from chunking.chunk import process_pdf_to_chunks
process_pdf_to_chunks("path/to/nasa_systems_engineering_handbook.pdf")
```

Then ingest the resulting `chunks.jsonl` into Weaviate:

```python
from ingestion.ingest import ingest
ingest()
```

> **Note:** Update the path in `ingestion/ingest.py` to point to your local `chunks.jsonl` before ingesting.

### 2. Web Interface (Streamlit)

```bash
streamlit run app.py
```

The web UI provides:
- A chat panel for asking questions
- A retrieval debug panel showing the top-10 retrieved chunks with similarity scores and metadata

### 3. CLI Interface

```bash
python main.py
```

Enter a question at the prompt and receive a cited answer in the terminal.

---

## Document Source

| Field | Value |
|-------|-------|
| Document | NASA Systems Engineering Handbook |
| Version | SP-2016-6105 Rev2 |
| Pages | ~270 pages, 17 chapters + appendices |
| License | U.S. Government work — public domain |
| Source | [nasa.gov](https://www.nasa.gov/wp-content/uploads/2018/09/nasa_systems_engineering_handbook_0.pdf) |

---

## Key Design Decisions

| Challenge | Approach |
|-----------|----------|
| Arbitrary chunk cuts break context | Section-boundary-aware splitting using regex header detection |
| Cross-chapter references | References extracted per chunk and stored as metadata |
| Long-range context (tables, appendices) | Hierarchical `path` metadata preserves parent section context |
| Acronym-heavy text (TRL, KDP, SRR, PDR, CDR) | LLM prompted to resolve acronyms from context before answering |
| Reranking quality | Cohere reranker applied after hybrid vector+keyword retrieval |
| Citation precision | Chunks carry `page_number`, `section`, and `title` — all surfaced in answers |

---

## Known Limitations

- Image/diagram descriptions are extracted as base64 but visual interpretation via a vision model is not yet integrated
- The ingestion path in `ingestion/ingest.py` is currently hardcoded and must be updated for your environment
- Multi-hop reasoning (e.g., connecting Chapter 6.6 to Chapter 6.8 in a single query) depends on both chunks being retrieved in the top-10 results