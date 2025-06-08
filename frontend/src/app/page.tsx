import ContractAnalyzer from './components/ContractAnalyzer';
import { Shield, FileText, Zap, Search } from 'lucide-react';

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-b from-gray-50 to-white dark:from-gray-900 dark:to-gray-800">
      {/* Hero Section */}
      <div className="relative overflow-hidden">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-16 text-center">
          <h1 className="text-5xl md:text-6xl font-bold text-gray-900 dark:text-white mb-6">
            Smart Contract Analyzer
          </h1>
          <p className="text-xl md:text-2xl text-gray-600 dark:text-gray-300 max-w-3xl mx-auto mb-8">
            AI-powered analysis for your smart contracts. Get instant insights, risk assessments, and expert-level understanding.
          </p>
          
          {/* Feature Highlights */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mt-16 mb-20">
            <div className="p-6 rounded-2xl bg-white dark:bg-gray-800 shadow-lg border border-gray-100 dark:border-gray-700">
              <Shield className="h-12 w-12 text-blue-500 mb-4 mx-auto" />
              <h3 className="text-xl font-semibold mb-2 text-gray-900 dark:text-white">Risk Assessment</h3>
              <p className="text-gray-600 dark:text-gray-300">Identify potential vulnerabilities and security risks in your contracts</p>
            </div>
            <div className="p-6 rounded-2xl bg-white dark:bg-gray-800 shadow-lg border border-gray-100 dark:border-gray-700">
              <FileText className="h-12 w-12 text-green-500 mb-4 mx-auto" />
              <h3 className="text-xl font-semibold mb-2 text-gray-900 dark:text-white">Smart Analysis</h3>
              <p className="text-gray-600 dark:text-gray-300">Get detailed explanations of complex contract clauses in plain English</p>
            </div>
            <div className="p-6 rounded-2xl bg-white dark:bg-gray-800 shadow-lg border border-gray-100 dark:border-gray-700">
              <Search className="h-12 w-12 text-purple-500 mb-4 mx-auto" />
              <h3 className="text-xl font-semibold mb-2 text-gray-900 dark:text-white">Deep Insights</h3>
              <p className="text-gray-600 dark:text-gray-300">Ask questions and get comprehensive answers about your contracts</p>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-20">
        <ContractAnalyzer />
      </div>
    </main>
  );
}