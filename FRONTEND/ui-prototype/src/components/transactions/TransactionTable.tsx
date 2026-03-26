import React, { useState, useMemo } from 'react';
import { Search, Filter, Download, Edit2, MessageSquare, Flag, ChevronLeft, ChevronRight, ChevronsUpDown } from 'lucide-react';
import toast from 'react-hot-toast';
import { Card } from '../ui/Card';
import { Button } from '../ui/Button';
import { Badge } from '../ui/Badge';
import { useAppContext } from '../../context/AppContext';
import './TransactionTable.css';

export const TransactionTable: React.FC = () => {
  const { transactions } = useAppContext();
  const [searchTerm, setSearchTerm] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [amountFilter, setAmountFilter] = useState(0);
  const [categoryFilter, setCategoryFilter] = useState('');
  const [dateFilterActive, setDateFilterActive] = useState(false);
  
  const rowsPerPage = 5;

  const categories = useMemo(() => Array.from(new Set(transactions.map(t => t.category))), [transactions]);

  const filteredTransactions = transactions.filter(t => {
    const matchesSearch = t.description.toLowerCase().includes(searchTerm.toLowerCase()) || 
                          t.category.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesAmount = t.amount >= amountFilter;
    const matchesCategory = categoryFilter ? t.category === categoryFilter : true;
    
    let matchesDate = true;
    if (dateFilterActive) {
      const txDate = new Date(t.date);
      const thirtyDaysAgo = new Date();
      thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
      matchesDate = txDate >= thirtyDaysAgo;
    }
    
    return matchesSearch && matchesAmount && matchesCategory && matchesDate;
  });

  const totalPages = Math.ceil(filteredTransactions.length / rowsPerPage);
  const displayedTransactions = filteredTransactions.slice(
    (currentPage - 1) * rowsPerPage, 
    currentPage * rowsPerPage
  );

  const handleReset = () => {
    setSearchTerm('');
    setAmountFilter(0);
    setCategoryFilter('');
    setDateFilterActive(false);
    setCurrentPage(1);
  };

  const handleRowAction = (actionName: string, id: string) => {
    toast.success(`${actionName} action triggered for reference ${id}`);
  };

  const handleExportCSV = () => {
    if (!transactions.length) return;
    const header = ['Date', 'Description', 'Category', 'Payment Mode', 'Amount', 'Is Anomaly'];
    const csvContent = transactions.map(t => 
      `"${t.date}","${t.description}","${t.category}","${t.mode}",${t.amount},${t.isAnomaly}`
    );
    const csvBlob = new Blob([header.join(',') + '\\n' + csvContent.join('\\n')], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(csvBlob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', 'financial_transactions_export.csv');
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="transactions-container animate-fade-in">
      <div className="section-header">
        <h2 className="section-title">Transactions</h2>
        <p className="section-subtitle text-secondary">Review and categorize your recent spending.</p>
      </div>

      <Card className="filter-bar-card">
        <div className="filter-bar">
          <div className="filter-group search-group">
            <Search size={16} className="text-secondary" />
            <input 
              type="text" 
              placeholder="Search by description or category..." 
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>

          <div className="filter-divider"></div>

          <div className="filter-group options-group">
            <button 
              className={`filter-btn ${dateFilterActive ? 'bg-bg text-primary border-primary' : ''}`}
              onClick={() => { setDateFilterActive(!dateFilterActive); setCurrentPage(1); }}
            >
              <CalendarIcon size={16} />
              <span>Last 30 Days</span>
            </button>
            <div className="filter-btn" style={{ position: 'relative' }}>
              <Filter size={16} />
              <select 
                value={categoryFilter}
                onChange={e => { setCategoryFilter(e.target.value); setCurrentPage(1); }}
                style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', opacity: 0, cursor: 'pointer' }}
              >
                <option value="">All Categories</option>
                {categories.map(c => <option key={c as string} value={c as string}>{c as string}</option>)}
              </select>
              <span>{categoryFilter || 'Categories'}</span>
            </div>
            <div className="amount-range flex items-center gap-2 ml-2">
              <span className="text-sm text-secondary whitespace-nowrap">Min ₹{amountFilter}</span>
              <input 
                type="range" 
                min="0" 
                max="3000" 
                step="100"
                value={amountFilter}
                onChange={(e) => { setAmountFilter(parseInt(e.target.value)); setCurrentPage(1); }}
                className="slider" 
              />
            </div>
          </div>

          <div className="filter-actions ml-auto">
            <Button variant="ghost" size="sm" onClick={handleReset}>Reset</Button>
            <Button variant="secondary" size="sm" icon={<Download size={14} />} onClick={handleExportCSV}>Export CSV</Button>
          </div>
        </div>
      </Card>

      <Card className="table-card">
        <div className="table-responsive">
          <table className="data-table">
            <thead>
              <tr>
                <th>
                  <div className="th-content">
                    Date <ChevronsUpDown size={14} />
                  </div>
                </th>
                <th>Description</th>
                <th>
                  <div className="th-content">
                    Category <ChevronsUpDown size={14} />
                  </div>
                </th>
                <th>Payment Mode</th>
                <th>
                  <div className="th-content justify-end">
                    Amount <ChevronsUpDown size={14} />
                  </div>
                </th>
                <th align="center">Actions</th>
              </tr>
            </thead>
            <tbody>
              {displayedTransactions.map(tx => (
                <tr key={tx.id} className={tx.isAnomaly ? 'bg-alert-light' : ''}>
                  <td className="text-secondary">{tx.date}</td>
                  <td className="font-medium">
                    {tx.description}
                    {tx.isAnomaly && <Badge variant="alert" className="ml-2 py-0 px-1 text-[10px]">Anomaly</Badge>}
                  </td>
                  <td>
                    <Badge variant="neutral">{tx.category}</Badge>
                  </td>
                  <td className="text-secondary">{tx.mode}</td>
                  <td align="right" className={`amount-cell ${tx.amount > 1000 ? 'font-bold' : ''}`}>
                    ₹{tx.amount.toFixed(2)}
                  </td>
                  <td align="center">
                    <div className="row-actions">
                      <button className="action-icon" title="Edit Category" onClick={() => handleRowAction('Edit', tx.id)}><Edit2 size={16} /></button>
                      <button className="action-icon" title="Add Note" onClick={() => handleRowAction('Comment', tx.id)}><MessageSquare size={16} /></button>
                      <button className={`action-icon ${tx.isAnomaly ? 'text-alert' : ''}`} title="Flag Issue" onClick={() => handleRowAction('Flag', tx.id)}>
                        <Flag size={16} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="pagination">
          <span className="pagination-info">
            Showing {(currentPage - 1) * rowsPerPage + 1} to {Math.min(currentPage * rowsPerPage, filteredTransactions.length)} of {filteredTransactions.length} entries
          </span>
          <div className="pagination-controls">
            <button 
              className="page-btn" 
              disabled={currentPage === 1}
              onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
            >
              <ChevronLeft size={16} />
            </button>
            <span className="page-number">{currentPage}</span>
            <button 
              className="page-btn" 
              disabled={currentPage === totalPages || totalPages === 0}
              onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
            >
              <ChevronRight size={16} />
            </button>
          </div>
        </div>
      </Card>
    </div>
  );
};

// Simple helper icon
const CalendarIcon = ({ size }: { size: number }) => (
  <svg xmlns="http://www.w3.org/2000/svg" width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
    <line x1="16" y1="2" x2="16" y2="6"></line>
    <line x1="8" y1="2" x2="8" y2="6"></line>
    <line x1="3" y1="10" x2="21" y2="10"></line>
  </svg>
);
