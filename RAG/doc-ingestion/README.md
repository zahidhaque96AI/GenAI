Overview

Doc-ingestion is a Python-based project focused on building a Retrieval-Augmented Generation (RAG) system step by step, following production-oriented software engineering and architectural practices.

The initial phase focuses on developing a reliable document ingestion pipeline that can discover PDF documents, detect document changes, extract page-level text, and maintain document metadata and provenance.

The objective is to establish a structured and auditable foundation before introducing document chunking, embedding generation, vector storage, semantic retrieval, and LLM-based answer generation.

Current implementation status: Phase 1 – PDF Document Ingestion

This project is being developed incrementally, with an emphasis on clean architecture, separation of responsibilities, data validation, maintainability, and production-readiness.

Current Features

The current implementation provides the following capabilities:

1. PDF Discovery

Recursively discovers PDF documents from the configured input directory.

Supports PDF files with uppercase and lowercase extensions.

Processes documents in deterministic order.

Maintains relative file paths for document identification and provenance.

2. Incremental Document Processing

Calculates SHA-256 hashes to identify document content.

Detects newly added and modified PDF documents.

Skips documents whose content has not changed.

Uses document content hashes to generate stable document identifiers.

Removes previously stored page records for documents that are no longer present in the input directory.

3. PDF Text Extraction

Extracts text from PDF documents using pypdf.

Processes documents page by page.

Preserves page numbers and source file information.

Retains pages with empty extracted text so that documents requiring OCR can be identified.

4. Data Validation and Provenance

Uses Pydantic models to define and validate document-level and page-level data structures.

PdfManifestEntry

Maintains document-level information:

Document ID

Relative file path

SHA-256 content hash

Last modified timestamp

Page count

Extraction status

ExtractedPdfPage

Maintains page-level information:

Document ID

Relative file path

Page number

Extracted text

5. Persistent Ingestion Metadata

The ingestion pipeline maintains two data files:

manifest.json – Stores metadata about the currently discovered and processed PDF documents.

pages.jsonl – Stores extracted page-level records, with one JSON object per line.

These files are generated and maintained by the ingestion and storage components.

Architecture and Responsibilities

The implementation follows a modular structure with clearly separated responsibilities.

Module

Responsibility

ingest.py

Coordinates PDF discovery, change detection, extraction, and ingestion reconciliation.

pdf_extraction.py

Calculates SHA-256 hashes, generates document IDs, and extracts PDF page text.

models.py

Defines Pydantic models for document metadata and extracted page records.

storage.py

Handles loading and saving ingestion metadata and extracted page records.

Ingestion Workflow

Discover PDF documents from the configured input directory.

Calculate the SHA-256 hash of each document.

Compare the hash against the existing manifest.

Skip unchanged documents.

Generate a document ID for new or modified documents.

Extract text from each PDF page.

Create validated page and document metadata records.

Reconcile existing records with the currently discovered documents.

Persist the updated manifest and extracted page records.

Project Structure:

doc-ingestion/
│
├── pdfs/
│   └── sample.pdf
│
├── data/
│   ├── manifest.json
│   └── pages.jsonl
│
├── src/
│   ├── __init__.py
│   ├── ingest.py
│   ├── pdf_extraction.py
│   ├── models.py
│   └── storage.py
│
├── tests/
│
├── requirements.txt
├── README.md
└── .gitignore

Directory purpose:

pdfs/: Input directory containing source PDF documents.

data/: Persistent ingestion metadata and extracted page records.

src/: Application source code.

tests/: Unit and integration tests.

requirements.txt: Python project dependencies.
