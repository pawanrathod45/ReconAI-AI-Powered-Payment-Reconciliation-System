import { useState, useEffect } from 'react'
import { Play, Filter, Download, RefreshCw, AlertCircle, CheckCircle2 } from 'lucide-react'
import DataTable from '../components/DataTable'
import StatusBadge from '../components/StatusBadge'
import { getReconciliationResults, runReconciliation } from '../services/api'

const TABS = [
  { key: 'ALL', label: 'All Records' },
  { key: 'MATCHED', label: 'Matched' },
  { key: 'MISSING_SETTLEMENT', label: 'Unmatched Txns' },
  { key: 'TIMING_DIFFERENCE', label: 'Timing Differences' },
  { key: 'ROUNDING_DIFFERENCE', label: 'Rounding Differences' },
  { key: 'DUPLICATE', label: 'Duplicates' },
  { key: 'ORPHAN_REFUND', label: 'Orphan Refunds' },
  { key: 'UNMATCHED_SETTLEMENT', label: 'Unmatched Settlements' },
]

function formatINR(val) {
  if (val == null || val === '') return '-'
  const num = typeof val === 'string' ? parseFloat(val) : val
  if (isNaN(num)) return '-'
  return '₹' + num.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

export default function Reconciliation() {
  const [results, setResults] = useState([])
  const [activeTab, setActiveTab] = useState('ALL')
  const [loading, setLoading] = useState(true)
  const [running, setRunning] = useState(false)
  const [month, setMonth] = useState('10')
  const [year, setYear] = useState('2026')
  const [message, setMessage] = useState(null)
  const [error, setError] = useState(null)

  const fetchResults = async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await getReconciliationResults()
      setResults(Array.isArray(res.data) ? res.data : [])
    } catch (err) {
      setError('Failed to load reconciliation records. Make sure backend is running and data is loaded.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchResults()
  }, [])

  const handleRunReconciliation = async () => {
    setRunning(true)
    setMessage(null)
    setError(null)
    try {
      const res = await runReconciliation(parseInt(month), parseInt(year))
      setMessage('Reconciliation completed successfully!')
      await fetchResults()
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to run reconciliation.')
    } finally {
      setRunning(false)
    }
  }

  const filteredData = results.filter((item) => {
    if (activeTab === 'ALL') return true
    return item.status === activeTab
  })

  const columns = [
    {
      key: 'transaction_id',
      label: 'Txn ID',
      render: (row) => (
        <span className="font-mono text-xs font-semibold text-gray-900">
          {row.transaction_id || <span className="text-gray-400 font-normal">N/A</span>}
        </span>
      ),
    },
    {
      key: 'settlement_id',
      label: 'Settlement ID',
      render: (row) => (
        <span className="font-mono text-xs text-gray-700">
          {row.settlement_id || <span className="text-gray-400">N/A</span>}
        </span>
      ),
    },
    {
      key: 'transaction_amount',
      label: 'Txn Amount',
      render: (row) => (
        <span className="font-mono text-xs text-gray-900">
          {formatINR(row.transaction_amount)}
        </span>
      ),
    },
    {
      key: 'settlement_amount',
      label: 'Settlement Amount',
      render: (row) => (
        <span className="font-mono text-xs text-gray-900">
          {formatINR(row.settlement_amount)}
        </span>
      ),
    },
    {
      key: 'variance',
      label: 'Variance',
      render: (row) => {
        const num = parseFloat(row.variance)
        const isZero = isNaN(num) || num === 0
        return (
          <span className={`font-mono text-xs font-medium ${isZero ? 'text-gray-500' : 'text-red-600'}`}>
            {formatINR(row.variance)}
          </span>
        )
      },
    },
    {
      key: 'status',
      label: 'Status',
      render: (row) => <StatusBadge status={row.status} />,
    },
    {
      key: 'explanation',
      label: 'Explanation / Audit Note',
      render: (row) => (
        <span className="text-xs text-gray-600 max-w-xs block truncate" title={row.explanation}>
          {row.explanation}
        </span>
      ),
    },
  ]

  // Counts for tabs
  const tabCounts = results.reduce((acc, item) => {
    acc[item.status] = (acc[item.status] || 0) + 1
    return acc
  }, {})

  return (
    <div className="space-y-6">
      {/* Header & Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 bg-white p-5 rounded-xl border border-gray-100 shadow-sm">
        <div>
          <h1 className="text-xl font-bold text-gray-900">Payment Reconciliation</h1>
          <p className="text-xs text-gray-500 mt-1">
            Automated matching engine comparing transaction ledgers against bank batch settlements.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <div className="flex items-center gap-2">
            <select
              value={month}
              onChange={(e) => setMonth(e.target.value)}
              className="text-xs border border-gray-300 rounded-lg px-2.5 py-2 bg-white text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="10">October</option>
              <option value="11">November</option>
              <option value="12">December</option>
            </select>
            <select
              value={year}
              onChange={(e) => setYear(e.target.value)}
              className="text-xs border border-gray-300 rounded-lg px-2.5 py-2 bg-white text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="2026">2026</option>
              <option value="2025">2025</option>
            </select>
          </div>

          <button
            onClick={handleRunReconciliation}
            disabled={running}
            className="flex items-center gap-1.5 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold rounded-lg shadow-sm transition-colors disabled:opacity-50"
          >
            {running ? (
              <>
                <RefreshCw size={14} className="animate-spin" />
                <span>Running Engine...</span>
              </>
            ) : (
              <>
                <Play size={14} />
                <span>Run Reconciliation</span>
              </>
            )}
          </button>
        </div>
      </div>

      {message && (
        <div className="flex items-center gap-2 p-3 bg-emerald-50 border border-emerald-200 text-emerald-800 rounded-lg text-xs font-medium">
          <CheckCircle2 size={16} className="text-emerald-600 flex-shrink-0" />
          <span>{message}</span>
        </div>
      )}

      {error && (
        <div className="flex items-center gap-2 p-3 bg-red-50 border border-red-200 text-red-800 rounded-lg text-xs font-medium">
          <AlertCircle size={16} className="text-red-600 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Tabs */}
      <div className="border-b border-gray-200 bg-white px-3 pt-2 rounded-t-xl">
        <nav className="flex space-x-2 overflow-x-auto pb-2 scrollbar-none" aria-label="Tabs">
          {TABS.map((tab) => {
            const count = tab.key === 'ALL' ? results.length : (tabCounts[tab.key] || 0)
            const isActive = activeTab === tab.key
            return (
              <button
                key={tab.key}
                onClick={() => setActiveTab(tab.key)}
                className={`flex items-center gap-2 px-3 py-2 text-xs font-medium rounded-lg whitespace-nowrap transition-colors ${
                  isActive
                    ? 'bg-slate-900 text-white'
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                }`}
              >
                <span>{tab.label}</span>
                <span
                  className={`text-[10px] px-1.5 py-0.5 rounded-full font-mono ${
                    isActive ? 'bg-slate-700 text-white' : 'bg-gray-200 text-gray-700'
                  }`}
                >
                  {count}
                </span>
              </button>
            )
          })}
        </nav>
      </div>

      {/* Results Table */}
      <div className="bg-white rounded-b-xl shadow-sm border border-gray-100 p-4">
        <DataTable
          columns={columns}
          data={filteredData}
          loading={loading}
          emptyMessage="No reconciliation records found in this category. Click 'Run Reconciliation' or generate sample data in Upload page."
          pageSize={10}
        />
      </div>
    </div>
  )
}
