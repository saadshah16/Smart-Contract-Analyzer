'use client';

import { useState } from 'react';
import { Upload, FileText, AlertTriangle, CheckCircle, XCircle, Loader2, Moon, Sun, List, Plus } from 'lucide-react';
import mammoth from 'mammoth';
import ContractList from './ContractList';

interface Contract {
  id: string;
  name: string;
  address?: string;
  network?: string;
  addedAt: string;
  lastAnalyzed?: string;
}

export default function ContractAnalyzer() {
  const [contractText, setContractText] = useState('');
  const [contractName, setContractName] = useState('');
  const [contractAddress, setContractAddress] = useState('');
  const [network, setNetwork] = useState('');
  const [question, setQuestion] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [addSuccess, setAddSuccess] = useState<string | null>(null);
  const [queryResult, setQueryResult] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [theme, setTheme] = useState<'light' | 'dark'>(typeof window !== 'undefined' && window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
  const [showContractList, setShowContractList] = useState(false);
  const [selectedContract, setSelectedContract] = useState<Contract | null>(null);
  const [analysisResult, setAnalysisResult] = useState<any[] | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  // Toggle dark mode
  const toggleTheme = () => setTheme(theme === 'dark' ? 'light' : 'dark');

  // Toggle contract list view
  const toggleContractList = () => setShowContractList(!showContractList);

  // Handle contract selection
  const handleSelectContract = (contract: Contract) => {
    setSelectedContract(contract);
    setShowContractList(false);
    fetchAnalysis(contract.name);
  };

  // Handle contract file upload (PDF, DOCX, TXT, SOL)
  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setError(null);
    setContractText('');
    
    // Ensure this code only runs on the client side
    if (typeof window === 'undefined') {
      return; // Don't run on server
    }

    try {
      if (file.name.endsWith('.pdf')) {
        // Dynamically import pdfjs-dist only on the client side
        const pdfjsLib = await import('pdfjs-dist');
        
        (pdfjsLib as any).GlobalWorkerOptions.workerSrc = "/pdf.worker.min.js";
        
        const arrayBuffer = await file.arrayBuffer();
        const pdf = await pdfjsLib.getDocument({ data: arrayBuffer }).promise;
        let text = '';
        for (let i = 1; i <= pdf.numPages; i++) {
          const page = await pdf.getPage(i);
          const content = await page.getTextContent();
          text += content.items.map((item: any) => item.str).join(' ') + '\n';
        }
        setContractText(text.trim());
      } else if (file.name.endsWith('.docx')) {
        // DOCX extraction
        const arrayBuffer = await file.arrayBuffer();
        const result = await mammoth.extractRawText({ arrayBuffer });
        setContractText(result.value.trim());
      } else if (file.name.endsWith('.sol') || file.name.endsWith('.txt')) {
        // Plain text
        const reader = new FileReader();
        reader.onload = (event) => {
          setContractText(event.target?.result as string);
        };
        reader.readAsText(file);
      } else {
        setError('Unsupported file type. Please upload a .sol, .txt, .pdf, or .docx file.');
      }
    } catch (err: any) {
      setError('Failed to extract text: ' + (err.message || err));
    }
  };

  // Add contract to backend
  const handleAddContract = async () => {
    setIsLoading(true);
    setError(null);
    setAddSuccess(null);
    setQueryResult(null);
    try {
      const response = await fetch('http://localhost:8000/rag/add-contract', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          contract_text: contractText,
          contract_name: contractName,
          contract_address: contractAddress,
          network: network,
        }),
      });
      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Failed to add contract');
      }
      setAddSuccess('Contract added successfully!');
    } catch (err: any) {
      setError(err.message || 'Failed to add contract');
    } finally {
      setIsLoading(false);
    }
  };

  // Query backend
  const handleQuery = async () => {
    setIsLoading(true);
    setError(null);
    setQueryResult(null);
    try {
      const response = await fetch('http://localhost:8000/rag/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question: question,
          contract_name: selectedContract ? selectedContract.name : undefined,
        }),
      });
      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Failed to get answer');
      }
      const data = await response.json();
      setQueryResult(data.answer);
    } catch (err: any) {
      setError(err.message || 'Failed to get answer');
    } finally {
      setIsLoading(false);
    }
  };

  // Fetch analysis results for a stored contract
  const fetchAnalysis = async (contractName: string) => {
    setIsAnalyzing(true);
    setAnalysisResult(null); // Clear previous analysis
    setError(null); // Clear previous error
    try {
      const response = await fetch('http://localhost:8000/rag/analyze-stored', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ contract_name: contractName }),
      });
      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Failed to fetch analysis');
      }
      const data = await response.json();
      setAnalysisResult(data.analysis);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch analysis');
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <div className={`min-h-screen ${theme === 'dark' ? 'bg-gray-900 text-gray-100' : 'bg-gray-50 text-gray-900'} transition-colors duration-300`}>
      <div className="flex justify-between items-center p-4">
        <button
          onClick={toggleContractList}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg ${
            theme === 'dark' 
              ? 'bg-gray-800 hover:bg-gray-700' 
              : 'bg-white hover:bg-gray-100'
          } border border-gray-200 dark:border-gray-700 transition-colors`}
        >
          {showContractList ? <Plus className="h-5 w-5" /> : <List className="h-5 w-5" />}
          {showContractList ? 'New Contract' : 'View Contracts'}
        </button>
        <button
          onClick={toggleTheme}
          className="rounded-full p-2 border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
          aria-label="Toggle dark mode"
        >
          {theme === 'dark' ? <Sun className="h-5 w-5 text-yellow-400" /> : <Moon className="h-5 w-5 text-gray-700" />}
        </button>
      </div>

      {showContractList ? (
        <div className="max-w-7xl mx-auto p-4">
          <h2 className="text-2xl font-bold mb-4">Analyzed Contracts</h2>
          <ContractList onSelectContract={handleSelectContract} theme={theme} />
        </div>
      ) : (
        <div className="max-w-2xl mx-auto p-6 mt-4 rounded-2xl shadow-xl bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700">
          <h2 className="text-3xl font-bold mb-2 text-center">
            Smart Contract Analyzer <span className="text-blue-600 dark:text-blue-400">(RAG)</span>
          </h2>
          {selectedContract ? (
            <div className="">
              <div className={`mb-6 p-4 rounded-lg border ${
                theme === 'dark' ? 'bg-gray-700 border-gray-600' : 'bg-gray-100 border-gray-200'
              }`}>
                <h3 className="text-xl font-semibold mb-2">Contract Details</h3>
                <p><span className="font-medium">Name:</span> {selectedContract.name}</p>
                {selectedContract.address && <p><span className="font-medium">Address:</span> {selectedContract.address}</p>}
                {selectedContract.network && <p><span className="font-medium">Network:</span> {selectedContract.network}</p>}
                <p><span className="font-medium">Added:</span> {new Date(selectedContract.addedAt).toLocaleDateString()}</p>
                {/* Add more contract details here if available */}
              </div>
              
              {/* Analysis Results Section */}
              <div className={`mt-6 p-4 rounded-lg border ${
                theme === 'dark' ? 'bg-gray-700 border-gray-600' : 'bg-gray-100 border-gray-200'
              }`}>
                <h3 className="text-xl font-semibold mb-2">Analysis Results</h3>
                {isAnalyzing ? (
                  <div className="flex items-center justify-center py-4">
                    <Loader2 className="animate-spin h-8 w-8 mr-3 text-blue-500" />
                    Analyzing contract...
                  </div>
                ) : analysisResult && analysisResult.length > 0 ? (
                  analysisResult.map((clause, index) => (
                    <div key={index} className={`mb-4 p-3 border-b ${
                       theme === 'dark' ? 'border-gray-600' : 'border-gray-200'
                    }`}>
                      <p className="font-semibold mb-1">Clause {clause.clause_number}:</p>
                      <p className="text-sm text-gray-700 dark:text-gray-300 mb-2">Original: {clause.original_clause}</p>
                      <p className="mb-1">Explanation: {clause.explanation}</p>
                      {clause.risk_flag === 'Yes' && (
                        <p className="text-red-600 dark:text-red-400 font-medium">
                          Risk: {clause.risk_reason || 'Not specified'}
                        </p>
                      )}
                    </div>
                  ))
                ) : ( !isAnalyzing && !error && (
                  <div className="text-gray-500 dark:text-gray-400">No analysis results available yet for this contract.</div>
                ))}
              </div>
              
              {/* Query Section - Now for the selected contract */}
              <div className="mt-8 mb-4">
                <label className="block font-semibold mb-1">Ask a Question about {selectedContract.name}</label>
                <input
                  className="w-full border rounded p-2 mb-2 bg-gray-50 dark:bg-gray-900 border-gray-300 dark:border-gray-700 text-gray-900 dark:text-gray-100"
                  placeholder={`e.g. What does the mint function do in ${selectedContract.name}?`}
                  value={question}
                  onChange={e => setQuestion(e.target.value)}
                />
                <button
                  className="w-full bg-green-600 dark:bg-green-500 text-white px-4 py-2 rounded-lg font-semibold hover:bg-green-700 dark:hover:bg-green-600 disabled:opacity-50 transition-colors"
                  onClick={handleQuery}
                  disabled={isLoading || !question}
                >
                  {isLoading ? <Loader2 className="animate-spin h-5 w-5 inline mr-2" /> : null}
                  {isLoading ? 'Querying...' : 'Get Answer'}
                </button>
              </div>
              
              {/* Results & Errors */}
              {queryResult && (
                <div className="bg-gray-100 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded p-4 mt-4">
                  <h3 className="font-bold mb-2">Answer:</h3>
                  <pre className="whitespace-pre-wrap text-gray-800 dark:text-gray-100">{queryResult}</pre>
                </div>
              )}
              {error && (
                <div className="bg-red-50 dark:bg-red-900 border border-red-200 dark:border-red-700 rounded p-4 mt-4 text-red-700 dark:text-red-300">
                  <XCircle className="inline h-5 w-5 mr-1 text-red-500 dark:text-red-300" />
                  {error}
                </div>
              )}
            </div>
          ) : (
            <>
              <p className="text-center text-gray-500 dark:text-gray-300 mb-6">
                Upload your contract as .sol, .txt, .pdf, or .docx. Review the extracted text before submitting.
              </p>
              {/* Contract Upload Section */}
              <div className="mb-4">
                <label className="block font-semibold mb-1">Contract Text</label>
                <textarea
                  className="w-full border rounded p-2 mb-2 bg-gray-50 dark:bg-gray-900 border-gray-300 dark:border-gray-700 text-gray-900 dark:text-gray-100"
                  rows={8}
                  value={contractText}
                  onChange={e => setContractText(e.target.value)}
                  placeholder="Paste your smart contract code here or upload a file below"
                />
                <input type="file" accept=".sol,.txt,.pdf,.docx" onChange={handleFileChange} className="mb-2" />
                <p className="text-xs text-gray-500 dark:text-gray-400">Supported: .sol, .txt, .pdf, .docx</p>
              </div>
              <div className="mb-4 grid grid-cols-1 md:grid-cols-3 gap-2">
                <input
                  className="border rounded p-2 bg-gray-50 dark:bg-gray-900 border-gray-300 dark:border-gray-700 text-gray-900 dark:text-gray-100"
                  placeholder="Contract Name"
                  value={contractName}
                  onChange={e => setContractName(e.target.value)}
                />
                <input
                  className="border rounded p-2 bg-gray-50 dark:bg-gray-900 border-gray-300 dark:border-gray-700 text-gray-900 dark:text-gray-100"
                  placeholder="Contract Address (optional)"
                  value={contractAddress}
                  onChange={e => setContractAddress(e.target.value)}
                />
                <input
                  className="border rounded p-2 bg-gray-50 dark:bg-gray-900 border-gray-300 dark:border-gray-700 text-gray-900 dark:text-gray-100"
                  placeholder="Network (optional)"
                  value={network}
                  onChange={e => setNetwork(e.target.value)}
                />
              </div>
              <button
                className="w-full bg-blue-600 dark:bg-blue-500 text-white px-4 py-2 rounded-lg font-semibold hover:bg-blue-700 dark:hover:bg-blue-600 disabled:opacity-50 transition-colors"
                onClick={handleAddContract}
                disabled={isLoading || !contractText || !contractName}
              >
                {isLoading ? <Loader2 className="animate-spin h-5 w-5 inline mr-2" /> : null}
                {isLoading ? 'Adding...' : 'Add Contract'}
              </button>
              {addSuccess && <div className="text-green-600 dark:text-green-400 mt-2 text-center">{addSuccess}</div>}
            </>
          )}
        </div>
      )}
    </div>
  );
}