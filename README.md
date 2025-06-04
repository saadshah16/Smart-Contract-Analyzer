# Smart Contract Analyzer

## Overview
This project is a "Smart Contract Analyzer" (using FastAPI (backend) and React (frontend)) that leverages Retrieval-Augmented Generation (RAG) (via ChromaDB and Sentence Transformers) to analyze smart contracts and answer questions about them. It includes a "Knowledge Base" (stored in ChromaDB) for enhanced analysis context, such as security patterns and vulnerabilities.

The application allows users to upload new contracts for analysis, view a list of previously analyzed contracts, access detailed analysis results for stored contracts, and ask targeted questions about specific contracts using the RAG system.

## Features
- **Backend (FastAPI):**
  – Upload new smart contracts (PDF, DOCX, TXT, SOL) and extract their text.
  – "Analyze" the contract text using Claude (via Anthropic) to generate clause-by-clause explanations and risks.
  – Store contract chunks and metadata in ChromaDB for RAG.
  – Retrieve and reconstruct stored contract text for re-analysis.
  – Answer questions about contracts using RAG, incorporating context from stored contracts and the knowledge base.
  – "Manage" (add, reset, query) a "Knowledge Base" of smart contract security patterns, vulnerabilities, and token standards.
  – Provide statistics on stored contracts.
– **Frontend (React (Next.js)):**
  – "Upload" (or "paste") new smart contracts via a modern, responsive UI (using Tailwind CSS).
  – View a list of previously analyzed contracts.
  – Select a stored contract to view its details and analysis results.
  – Ask targeted questions about the currently selected contract.
  – View RAG-generated answers and analysis explanations.
  – Toggle between light and dark themes.

## How to Run (or "Demo")
### Backend (FastAPI)
1.  Ensure you have Python (and pip) installed.
2.  Clone (or "download") the repo (e.g., `git clone https://github.com/yourusername/smart-contract-analyzer.git`).
3.  Navigate (or "cd") into the `backend` folder (e.g., `cd smart-contract-analyzer/backend`).
4.  Install (or "pip install") the requirements (e.g., `pip install -r requirements.txt`).
5.  Set (or "export") your `ANTHROPIC_API_KEY` (e.g., `export ANTHROPIC_API_KEY=your_api_key_here` or `echo ANTHROPIC_API_KEY=your_api_key_here >> .env`).
6.  Run (or "python") the backend server (e.g., `uvicorn main:app --reload`). The API will be available at `http://localhost:8000`. You can view the API documentation at `http://localhost:8000/docs`.

### Frontend (React (Next.js))
1.  Ensure you have Node (and npm or "yarn") installed.
2.  Navigate (or "cd") into the `frontend` folder (e.g., `cd smart-contract-analyzer/frontend`).
3.  Install (or "npm install" or "yarn") the dependencies (e.g., `npm install` or `yarn`).
4.  Run (or "npm run dev" or "yarn dev") the frontend server (e.g., `npm run dev` or `yarn dev`). The UI will be available at `http://localhost:3000`.

## Usage
1.  **Analyze a New Contract:** Go to `http://localhost:3000`, upload or paste a smart contract, provide a name, and click "Add Contract".
2.  **View Analyzed Contracts:** Click the "View Contracts" button in the top left.
3.  **View Analysis of a Stored Contract:** From the list of analyzed contracts, click on a contract card to view its details and the AI-generated analysis results.
4.  **Query a Stored Contract:** While viewing a stored contract's details and analysis, use the "Ask a Question about [Contract Name]" section to ask questions about that specific contract.
5.  **Knowledge Base:** Run the test script (`python test_knowledge_base.py` in the `backend` directory) to add sample knowledge base items and see how they are used in RAG queries.

## GitHub Repo
– View the latest code on GitHub: `https://github.com/saadshah16/Smart-Contract-Analyzer`.
