import ContractAnalyzer from './components/ContractAnalyzer';

export default function Home() {
  return (
    <main className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Smart Contract Analyzer
          </h1>
          <p className="text-xl text-gray-600">
            Upload your legal contract and get AI-powered analysis
          </p>
        </div>
        <ContractAnalyzer />
      </div>
    </main>
  );
}