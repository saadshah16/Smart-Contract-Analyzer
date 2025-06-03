# Smart Contract Analyzer

This project is an AI-powered tool designed to help users understand complex smart contracts. It features a Retrieval-Augmented Generation (RAG) system that processes contract documents and allows users to ask questions about their content.

**Key Features:**

*   **Document Upload:** Supports uploading smart contract text in various formats (e.g., Solidity files, text files, PDFs).
*   **RAG-based Querying:** Utilize a RAG system to find relevant information within the uploaded contract and generate answers to user questions.
*   **AI Analysis:** Leverages language models (like Anthropic's Claude) for breaking down contract text and answering queries.

**Technologies Used:**

*   **Backend:** FastAPI, LangChain, ChromaDB (for vector storage), Python
*   **Frontend:** Next.js, React, TypeScript
*   **AI Model:** Anthropic Claude

This project is currently under development, with ongoing work to enhance its capabilities, including adding conversation memory, improving document processing, and more.

## Getting Started

First, run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

You can start editing the page by modifying `app/page.tsx`. The page auto-updates as you edit the file.

This project uses [`next/font`](https://nextjs.org/docs/app/building-your-application/optimizing/fonts) to automatically optimize and load [Geist](https://vercel.com/font), a new font family for Vercel.

## Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js) - your feedback and contributions are welcome!

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.
