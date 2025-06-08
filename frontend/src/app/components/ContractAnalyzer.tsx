'use client';

import { useState } from 'react';
import { Upload, FileText, AlertTriangle, CheckCircle, XCircle, Loader2, Moon, Sun, List, Plus, Search, Zap, BarChart2 } from 'lucide-react';
import mammoth from 'mammoth';
import ContractList from './ContractList';
import AnalysisDashboard from './AnalysisDashboard';

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
  const [activeTab, setActiveTab] = useState<'analyzer' | 'dashboard'>('analyzer');

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
      {/* Navigation Bar */}
      <div className="sticky top-0 z-50 backdrop-blur-lg bg-white/80 dark:bg-gray-900/80 border-b border-gray-200 dark:border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-4">
              <button
                onClick={() => setActiveTab('analyzer')}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all duration-200 ${
                  activeTab === 'analyzer'
                    ? theme === 'dark'
                      ? 'bg-gray-800 text-white'
                      : 'bg-gray-100 text-gray-900'
                    : theme === 'dark'
                    ? 'text-gray-400 hover:text-white'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                <FileText className="h-5 w-5" />
                <span className="font-medium">Analyzer</span>
              </button>
              <button
                onClick={() => setActiveTab('dashboard')}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all duration-200 ${
                  activeTab === 'dashboard'
                    ? theme === 'dark'
                      ? 'bg-gray-800 text-white'
                      : 'bg-gray-100 text-gray-900'
                    : theme === 'dark'
                    ? 'text-gray-400 hover:text-white'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                <BarChart2 className="h-5 w-5" />
                <span className="font-medium">Dashboard</span>
              </button>
              {activeTab === 'analyzer' && (
                <button
                  onClick={toggleContractList}
                  className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all duration-200 ${
                    theme === 'dark' 
                      ? 'bg-gray-800 hover:bg-gray-700 hover:shadow-lg' 
                      : 'bg-white hover:bg-gray-50 hover:shadow-lg'
                  } border border-gray-200 dark:border-gray-700`}
                >
                  {showContractList ? <Plus className="h-5 w-5" /> : <List className="h-5 w-5" />}
                  <span className="font-medium">{showContractList ? 'New Contract' : 'View Contracts'}</span>
                </button>
              )}
            </div>
            <button
              onClick={toggleTheme}
              className="rounded-full p-2 border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 hover:bg-gray-100 dark:hover:bg-gray-700 transition-all duration-200 hover:shadow-lg"
              aria-label="Toggle dark mode"
            >
              {theme === 'dark' ? <Sun className="h-5 w-5 text-yellow-400" /> : <Moon className="h-5 w-5 text-gray-700" />}
            </button>
          </div>
        </div>
      </div>

      {activeTab === 'dashboard' ? (
        <div className="max-w-7xl mx-auto p-6">
          <AnalysisDashboard theme={theme} />
        </div>
      ) : showContractList ? (
        <div className="max-w-7xl mx-auto p-4">
          <h2 className="text-2xl font-bold mb-4">Analyzed Contracts</h2>
          <ContractList onSelectContract={handleSelectContract} theme={theme} />
        </div>
      ) : (
        <div className="max-w-2xl mx-auto p-6 mt-4 rounded-2xl shadow-xl bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 transform transition-all duration-300 hover:shadow-2xl">
          <h2 className="text-3xl font-bold mb-2 text-center bg-gradient-to-r from-blue-600 to-purple-600 dark:from-blue-400 dark:to-purple-400 bg-clip-text text-transparent">
            Smart Contract Analyzer <span className="text-blue-600 dark:text-blue-400">(RAG)</span>
          </h2>
          {selectedContract ? (
            <div className="space-y-6">
              <div className={`p-6 rounded-xl border ${
                theme === 'dark' ? 'bg-gray-700/50 border-gray-600' : 'bg-gray-50 border-gray-200'
              } backdrop-blur-sm`}>
                <h3 className="text-xl font-semibold mb-4 flex items-center gap-2">
                  <FileText className="h-5 w-5 text-blue-500" />
                  Contract Details
                </h3>
                <div className="space-y-2">
                  <p className="flex items-center gap-2">
                    <span className="font-medium text-gray-500 dark:text-gray-400">Name:</span>
                    <span className="text-gray-900 dark:text-gray-100">{selectedContract.name}</span>
                  </p>
                  {selectedContract.address && (
                    <p className="flex items-center gap-2">
                      <span className="font-medium text-gray-500 dark:text-gray-400">Address:</span>
                      <span className="text-gray-900 dark:text-gray-100 font-mono">{selectedContract.address}</span>
                    </p>
                  )}
                  {selectedContract.network && (
                    <p className="flex items-center gap-2">
                      <span className="font-medium text-gray-500 dark:text-gray-400">Network:</span>
                      <span className="text-gray-900 dark:text-gray-100">{selectedContract.network}</span>
                    </p>
                  )}
                  <p className="flex items-center gap-2">
                    <span className="font-medium text-gray-500 dark:text-gray-400">Added:</span>
                    <span className="text-gray-900 dark:text-gray-100">{new Date(selectedContract.addedAt).toLocaleDateString()}</span>
                  </p>
                </div>
              </div>
              
              {/* Analysis Results Section */}
              <div className={`p-6 rounded-xl border ${
                theme === 'dark' ? 'bg-gray-700/50 border-gray-600' : 'bg-gray-50 border-gray-200'
              } backdrop-blur-sm`}>
                <h3 className="text-xl font-semibold mb-4 flex items-center gap-2">
                  <Search className="h-5 w-5 text-purple-500" />
                  Analysis Results
                </h3>
                {isAnalyzing ? (
                  <div className="flex items-center justify-center py-8">
                    <div className="flex flex-col items-center gap-3">
                      <Loader2 className="animate-spin h-8 w-8 text-blue-500" />
                      <span className="text-gray-500 dark:text-gray-400">Analyzing contract...</span>
                    </div>
                  </div>
                ) : analysisResult && analysisResult.length > 0 ? (
                  <div className="space-y-4">
                    {analysisResult.map((clause, index) => (
                      <div key={index} className={`p-4 rounded-lg border ${
                        theme === 'dark' ? 'bg-gray-800/50 border-gray-600' : 'bg-white border-gray-200'
                      } transition-all duration-200 hover:shadow-md`}>
                        <div className="flex items-start gap-3">
                          <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                            clause.risk_flag === 'Yes' ? 'bg-red-100 dark:bg-red-900/30' : 'bg-green-100 dark:bg-green-900/30'
                          }`}>
                            {clause.risk_flag === 'Yes' ? (
                              <AlertTriangle className="h-5 w-5 text-red-500" />
                            ) : (
                              <CheckCircle className="h-5 w-5 text-green-500" />
                            )}
                          </div>
                          <div className="flex-1">
                            <p className="font-semibold mb-2">Clause {clause.clause_number}</p>
                            <p className="text-sm text-gray-600 dark:text-gray-300 mb-2 font-mono bg-gray-50 dark:bg-gray-800 p-2 rounded">
                              {clause.original_clause}
                            </p>
                            <p className="text-gray-700 dark:text-gray-200">{clause.explanation}</p>
                            {clause.risk_flag === 'Yes' && (
                              <div className="mt-2 p-2 rounded bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800">
                                <p className="text-red-600 dark:text-red-400 font-medium flex items-center gap-2">
                                  <AlertTriangle className="h-4 w-4" />
                                  Risk: {clause.risk_reason || 'Not specified'}
                                </p>
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (!isAnalyzing && !error && (
                  <div className="text-center py-8 text-gray-500 dark:text-gray-400">
                    No analysis results available yet for this contract.
                  </div>
                ))}
              </div>
              
              {/* Query Section */}
              <div className="p-6 rounded-xl border bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700">
                <h3 className="text-xl font-semibold mb-4 flex items-center gap-2">
                  <Zap className="h-5 w-5 text-yellow-500" />
                  Ask a Question
                </h3>
                <div className="space-y-4">
                  <input
                    className="w-full border rounded-lg p-3 bg-gray-50 dark:bg-gray-900 border-gray-300 dark:border-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
                    placeholder={`e.g. What does the mint function do in ${selectedContract.name}?`}
                    value={question}
                    onChange={e => setQuestion(e.target.value)}
                  />
                  <button
                    className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white px-6 py-3 rounded-lg font-semibold transition-all duration-200 transform hover:scale-[1.02] disabled:opacity-50 disabled:hover:scale-100"
                    onClick={handleQuery}
                    disabled={isLoading || !question}
                  >
                    {isLoading ? (
                      <span className="flex items-center justify-center gap-2">
                        <Loader2 className="animate-spin h-5 w-5" />
                        Querying...
                      </span>
                    ) : (
                      'Get Answer'
                    )}
                  </button>
                </div>
              </div>
              
              {/* Results & Errors */}
              {queryResult && (
                <div className="p-6 rounded-xl border bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700">
                  <h3 className="text-xl font-semibold mb-4 flex items-center gap-2">
                    <FileText className="h-5 w-5 text-green-500" />
                    Answer
                  </h3>
                  <div className="prose dark:prose-invert max-w-none">
                    <pre className="whitespace-pre-wrap text-gray-800 dark:text-gray-100 bg-gray-50 dark:bg-gray-900 p-4 rounded-lg">
                      {queryResult}
                    </pre>
                  </div>
                </div>
              )}
              {error && (
                <div className="p-6 rounded-xl border bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800">
                  <div className="flex items-center gap-2 text-red-600 dark:text-red-400">
                    <XCircle className="h-5 w-5" />
                    <span className="font-medium">{error}</span>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="space-y-6">
              <p className="text-center text-gray-500 dark:text-gray-300 mb-6">
                Upload your contract as .sol, .txt, .pdf, or .docx. Review the extracted text before submitting.
              </p>
              
              {/* Contract Upload Section */}
              <div className="space-y-4">
                <div className="relative">
                  <textarea
                    className="w-full border rounded-lg p-4 bg-gray-50 dark:bg-gray-900 border-gray-300 dark:border-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
                    rows={8}
                    value={contractText}
                    onChange={e => setContractText(e.target.value)}
                    placeholder="Paste your smart contract code here or upload a file below"
                  />
                </div>
                
                <div className="flex items-center justify-center w-full">
                  <label className="flex flex-col items-center justify-center w-full h-32 border-2 border-gray-300 dark:border-gray-600 border-dashed rounded-lg cursor-pointer bg-gray-50 dark:bg-gray-900 hover:bg-gray-100 dark:hover:bg-gray-800 transition-all duration-200">
                    <div className="flex flex-col items-center justify-center pt-5 pb-6">
                      <Upload className="h-8 w-8 mb-3 text-gray-400" />
                      <p className="mb-2 text-sm text-gray-500 dark:text-gray-400">
                        <span className="font-semibold">Click to upload</span> or drag and drop
                      </p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">
                        .sol, .txt, .pdf, or .docx
                      </p>
                    </div>
                    <input
                      type="file"
                      className="hidden"
                      accept=".sol,.txt,.pdf,.docx"
                      onChange={handleFileChange}
                    />
                  </label>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <input
                  className="border rounded-lg p-3 bg-gray-50 dark:bg-gray-900 border-gray-300 dark:border-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
                  placeholder="Contract Name"
                  value={contractName}
                  onChange={e => setContractName(e.target.value)}
                />
                <input
                  className="border rounded-lg p-3 bg-gray-50 dark:bg-gray-900 border-gray-300 dark:border-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
                  placeholder="Contract Address (optional)"
                  value={contractAddress}
                  onChange={e => setContractAddress(e.target.value)}
                />
                <input
                  className="border rounded-lg p-3 bg-gray-50 dark:bg-gray-900 border-gray-300 dark:border-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
                  placeholder="Network (optional)"
                  value={network}
                  onChange={e => setNetwork(e.target.value)}
                />
              </div>

              <button
                className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white px-6 py-3 rounded-lg font-semibold transition-all duration-200 transform hover:scale-[1.02] disabled:opacity-50 disabled:hover:scale-100"
                onClick={handleAddContract}
                disabled={isLoading || !contractText || !contractName}
              >
                {isLoading ? (
                  <span className="flex items-center justify-center gap-2">
                    <Loader2 className="animate-spin h-5 w-5" />
                    Adding...
                  </span>
                ) : (
                  'Add Contract'
                )}
              </button>

              {addSuccess && (
                <div className="p-4 rounded-lg bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800">
                  <div className="flex items-center gap-2 text-green-600 dark:text-green-400">
                    <CheckCircle className="h-5 w-5" />
                    <span>{addSuccess}</span>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}