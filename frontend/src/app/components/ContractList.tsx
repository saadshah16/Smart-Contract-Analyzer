'use client';

import { useState, useEffect } from 'react';
import { FileText, Network, Hash, Calendar, Search, Filter } from 'lucide-react';

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
      // Transform the data into our Contract interface
      // Access contracts from the nested 'stats' object
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
      <div className={`p-4 rounded-lg ${theme === 'dark' ? 'bg-gray-800' : 'bg-gray-50'}`}>
        <div className="animate-pulse space-y-4">
          {[1, 2, 3].map(i => (
            <div key={i} className={`h-24 rounded-lg ${theme === 'dark' ? 'bg-gray-700' : 'bg-gray-200'}`} />
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`p-4 rounded-lg ${theme === 'dark' ? 'bg-red-900/50' : 'bg-red-50'} text-red-600 dark:text-red-400`}>
        Error loading contracts: {error}
      </div>
    );
  }

  return (
    <div className={`p-4 rounded-lg ${theme === 'dark' ? 'bg-gray-800' : 'bg-gray-50'}`}>
      {/* Search and Filter Bar */}
      <div className="mb-4 flex flex-col sm:flex-row gap-2">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search contracts..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className={`w-full pl-10 pr-4 py-2 rounded-lg border ${
              theme === 'dark' 
                ? 'bg-gray-700 border-gray-600 text-gray-100' 
                : 'bg-white border-gray-300 text-gray-900'
            }`}
          />
        </div>
        <select
          value={filterNetwork}
          onChange={(e) => setFilterNetwork(e.target.value)}
          className={`px-4 py-2 rounded-lg border ${
            theme === 'dark'
              ? 'bg-gray-700 border-gray-600 text-gray-100'
              : 'bg-white border-gray-300 text-gray-900'
          }`}
        >
          {networks.map(network => (
            <option key={network} value={network}>
              {network === 'all' ? 'All Networks' : network}
            </option>
          ))}
        </select>
      </div>

      {/* Contract Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filteredContracts.map(contract => (
          <button
            key={contract.id}
            onClick={() => onSelectContract(contract)}
            className={`p-4 rounded-lg border transition-all hover:shadow-lg ${
              theme === 'dark'
                ? 'bg-gray-700 border-gray-600 hover:bg-gray-600'
                : 'bg-white border-gray-200 hover:bg-gray-50'
            }`}
          >
            <div className="flex items-start gap-3">
              <FileText className={`h-6 w-6 ${theme === 'dark' ? 'text-blue-400' : 'text-blue-600'}`} />
              <div className="flex-1 text-left">
                <h3 className="font-semibold mb-1 truncate">{contract.name}</h3>
                {contract.address && (
                  <div className="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400 mb-1">
                    <Hash className="h-4 w-4" />
                    <span className="truncate">{contract.address}</span>
                  </div>
                )}
                {contract.network && (
                  <div className="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400 mb-1">
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
        <div className={`text-center py-8 text-gray-500 dark:text-gray-400 ${
          theme === 'dark' ? 'bg-gray-700/50' : 'bg-gray-100'
        } rounded-lg`}>
          No contracts found
        </div>
      )}
    </div>
  );
} 