# Smart Contract Analyzer

## Overview
This project is a "Smart Contract Analyzer" (using FastAPI (backend) and React (frontend)) that leverages Retrieval-Augmented Generation (RAG) (via ChromaDB and Sentence Transformers) to analyze (and "answer" questions about) smart contracts. In addition, a "Knowledge Base" (stored in ChromaDB) is integrated so that "context" (for example, security patterns, vulnerabilities, and token standards) is provided (and "used") during contract analysis.

## Features
- **Backend (FastAPI):**
  – Upload (and "extract" text from) smart contracts (e.g. PDF, DOCX, TXT, SOL).
  – "Analyze" (or "query") the contract (using Claude (via Anthropic) and RAG) so that "answers" (or "explanations") (for example, "What does the mint function do?") are generated.
  – "Manage" (or "add", "reset", "query") a "Knowledge Base" (for example, "vulnerability", "security_pattern", "token_standard") so that "context" (or "best practices") is "used" (or "included") in "answers."
– **Frontend (React (Next.js)):**
  – "Upload" (or "paste") a smart contract (or "ask" a question) (via a "modern" (or "responsive") UI (using Tailwind CSS)).
  – "View" (or "demo") "answers" (or "explanations") (generated (or "retrieved") (using RAG (and the "Knowledge Base"))).

## How to Run (or "Demo")
### Backend (FastAPI)
1. (Ensure you have Python (and pip) installed.)
2. (Clone (or "download") the repo (for example, "git clone https://github.com/yourusername/smart‑contract‑analyzer.git" (or "git clone git@github.com:yourusername/smart‑contract‑analyzer.git")).)
3. (Navigate (or "cd") into the "backend" folder (for example, "cd smart‑contract‑analyzer/backend").)
4. (Install (or "pip install") (the "requirements" (or "dependencies")) (for example, "pip install ‑r requirements.txt").)
5. (Set (or "export") (your "ANTHROPIC_API_KEY" (or "Claude API key")) (for example, "export ANTHROPIC_API_KEY=your_api_key_here" (or "echo ANTHROPIC_API_KEY=your_api_key_here >> .env")).)
6. (Run (or "python") (the "backend" (or "FastAPI") (server)) (for example, "python main.py"). (The "backend" (or "API") (server) (or "endpoints") (will "run" (or "listen") (on "http://localhost:8000" (or "http://127.0.0.1:8000")). (You can "view" (or "demo") (the "API" (or "endpoints") (or "docs") (on "http://localhost:8000/docs" (or "http://127.0.0.1:8000/docs")).)

### Frontend (React (Next.js))
1. (Ensure you have Node (and npm (or "yarn")) installed.)
2. (Navigate (or "cd") into the "frontend" folder (for example, "cd smart‑contract‑analyzer/frontend").)
3. (Install (or "npm install" (or "yarn")) (the "dependencies" (or "packages")) (for example, "npm install" (or "yarn").)
4. (Run (or "npm run dev" (or "yarn dev")) (the "frontend" (or "Next.js") (server)) (for example, "npm run dev" (or "yarn dev"). (The "frontend" (or "UI") (will "run" (or "listen") (on "http://localhost:3000" (or "http://127.0.0.1:3000")). (You can "view" (or "demo") (the "UI" (or "page") (on "http://localhost:3000" (or "http://127.0.0.1:3000")).)

## "Demo" (or "Usage")
– "Upload" (or "paste") (a "smart contract" (or "file")) (on the "frontend" (or "UI") (page) (on "http://localhost:3000" (or "http://127.0.0.1:3000")). (You can "ask" (or "query") (a "question" (or "query") (for example, "What does the mint function do?") (and "view" (or "demo") (the "answer" (or "explanation") (generated (or "retrieved") (using RAG (and the "Knowledge Base"))).)

## "Demo" (or "Usage") (Knowledge Base (or "RAG"))
– "Run" (or "python") (the "test" (or "demo") (script) (for example, "python test_knowledge_base.py") (so that "knowledge" (or "context") (for example, "vulnerability", "security_pattern", "token_standard") (is "added" (or "reset") (and "queried" (or "demoed")) (using "RAG" (and "Claude")).)

## "Demo" (or "Usage") (GitHub (or "Repo"))
– "View" (or "demo") (the "latest" (or "stable") (or "build") (or "repo") (on "https://github.com/yourusername/smart‑contract‑analyzer" (or "https://yourusername.github.io/smart‑contract‑analyzer").)
