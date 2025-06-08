'use client';

import { useState, useEffect } from 'react';
import { FileText, Network, Hash, Calendar, Search, Filter, Loader2, XCircle } from 'lucide-react';

interface Contract {
  id: string;
  name: string;
  address?: string;
  network?: string;
  addedAt: string;
  lastAnalyzed?: string;
}

interface ContractListProps {
  onSelectContract: (contract: Contract) => void;
  theme: 'light' | 'dark';
}

export default function ContractList({ onSelectContract, theme }: ContractListProps) {
  const [contracts, setContracts] = useState<Contract[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterNetwork, setFilterNetwork] = useState<string>('all');

  useEffect(() => {
    fetchContracts();
  }, []);

  const fetchContracts = async () => {
    try {
      const response = await fetch('http://localhost:8000/rag/stats');
      if (!response.ok) {
        throw new Error('Failed to fetch contracts');
      }
      const data = await response.json();
      const transformedContracts: Contract[] = data.stats?.contracts || [];
      setContracts(transformedContracts);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const filteredContracts = contracts.filter(contract => {
    const matchesSearch = contract.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         (contract.address?.toLowerCase().includes(searchTerm.toLowerCase()) ?? false);
    const matchesNetwork = filterNetwork === 'all' || contract.network === filterNetwork;
    return matchesSearch && matchesNetwork;
  });

  const networks = ['all', ...new Set(contracts.map(c => c.network).filter(Boolean))];

  if (isLoading) {
    return (
      <div className={`p-8 rounded-xl ${theme === 'dark' ? 'bg-gray-800/50' : 'bg-gray-50'}`}>
        <div className="animate-pulse space-y-6">
          {[1, 2, 3].map(i => (
            <div key={i} className={`h-32 rounded-xl ${theme === 'dark' ? 'bg-gray-700/50' : 'bg-gray-200/50'}`} />
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`p-6 rounded-xl ${theme === 'dark' ? 'bg-red-900/20' : 'bg-red-50'} border border-red-200 dark:border-red-800`}>
        <div className="flex items-center gap-2 text-red-600 dark:text-red-400">
          <XCircle className="h-5 w-5" />
          <span className="font-medium">Error loading contracts: {error}</span>
        </div>
      </div>
    );
  }

  return (
    <div className={`p-6 rounded-xl ${theme === 'dark' ? 'bg-gray-800/50' : 'bg-gray-50'} backdrop-blur-sm`}>
      {/* Search and Filter Bar */}
      <div className="mb-6 flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
          <input
            type="text"
            placeholder="Search contracts..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className={`w-full pl-12 pr-4 py-3 rounded-xl border ${
              theme === 'dark' 
                ? 'bg-gray-700/50 border-gray-600 text-gray-100 focus:border-blue-500' 
                : 'bg-white border-gray-300 text-gray-900 focus:border-blue-500'
            } focus:ring-2 focus:ring-blue-500/20 transition-all duration-200`}
          />
        </div>
        <div className="relative">
          <Filter className="absolute left-4 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
          <select
            value={filterNetwork}
            onChange={(e) => setFilterNetwork(e.target.value)}
            className={`pl-12 pr-8 py-3 rounded-xl border appearance-none ${
              theme === 'dark'
                ? 'bg-gray-700/50 border-gray-600 text-gray-100 focus:border-blue-500'
                : 'bg-white border-gray-300 text-gray-900 focus:border-blue-500'
            } focus:ring-2 focus:ring-blue-500/20 transition-all duration-200`}
          >
            {networks.map(network => (
              <option key={network} value={network}>
                {network === 'all' ? 'All Networks' : network}
              </option>
            ))}
          </select>
          <div className="absolute right-4 top-1/2 transform -translate-y-1/2 pointer-events-none">
            <svg className="h-4 w-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </div>
        </div>
      </div>

      {/* Contract Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredContracts.map(contract => (
          <button
            key={contract.id}
            onClick={() => onSelectContract(contract)}
            className={`p-6 rounded-xl border transition-all duration-200 hover:shadow-lg ${
              theme === 'dark'
                ? 'bg-gray-700/50 border-gray-600 hover:bg-gray-600/50'
                : 'bg-white border-gray-200 hover:bg-gray-50'
            }`}
          >
            <div className="flex items-start gap-4">
              <div className={`p-3 rounded-lg ${
                theme === 'dark' ? 'bg-blue-500/20' : 'bg-blue-100'
              }`}>
                <FileText className={`h-6 w-6 ${theme === 'dark' ? 'text-blue-400' : 'text-blue-600'}`} />
              </div>
              <div className="flex-1 text-left">
                <h3 className="font-semibold mb-2 text-lg truncate">{contract.name}</h3>
                {contract.address && (
                  <div className="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400 mb-2">
                    <Hash className="h-4 w-4" />
                    <span className="truncate font-mono">{contract.address}</span>
                  </div>
                )}
                {contract.network && (
                  <div className="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400 mb-2">
                    <Network className="h-4 w-4" />
                    <span>{contract.network}</span>
                  </div>
                )}
                <div className="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
                  <Calendar className="h-4 w-4" />
                  <span>Added {new Date(contract.addedAt).toLocaleDateString()}</span>
                </div>
              </div>
            </div>
          </button>
        ))}
      </div>

      {filteredContracts.length === 0 && (
        <div className={`text-center py-12 rounded-xl ${
          theme === 'dark' ? 'bg-gray-700/30' : 'bg-gray-100'
        }`}>
          <div className="flex flex-col items-center gap-3">
            <FileText className="h-12 w-12 text-gray-400" />
            <p className="text-gray-500 dark:text-gray-400">No contracts found</p>
            {searchTerm && (
              <p className="text-sm text-gray-400 dark:text-gray-500">
                Try adjusting your search or filters
              </p>
            )}
          </div>
        </div>
      )}
    </div>
  );
} 