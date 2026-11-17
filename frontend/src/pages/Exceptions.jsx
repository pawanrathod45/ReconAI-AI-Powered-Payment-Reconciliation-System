import { useState, useEffect } from 'react'
import { AlertTriangle, Clock, Calculator, Copy, FileX, HelpCircle, Loader2 } from 'lucide-react'
import DataTable from '../components/DataTable'
import StatusBadge from '../components/StatusBadge'
import { getExceptions } from '../services/api'

function formatINR(val) {
  if (val == null || val === '') return '-'
  const num = typeof val === 'string' ? parseFloat(val) : val
  if (isNaN(num)) return '-'
  return '₹' + num.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

export default function Exceptions() {
  const [exceptions, setExceptions] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const fetchExceptions = async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await getExceptions()
      setExceptions(Array.isArray(res.data) ? res.data : [])
    } catch (err) {
      setError('Failed to load exceptions. Please verify that reconciliation has been run.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchExceptions()
  }, [])

  const counts = exceptions.reduce((acc, item) => {
    acc[item.status] = (acc[item.status] || 0) + 1
    return acc
  }, {})

  const columns = [
    {
      key: 'status',
      label: 'Exception Type',
      render: (row) => <StatusBadge status={row.status} />,
    },
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
      render: (row) => (
        <span className="font-mono text-xs font-bold text-red-600">
          {formatINR(row.variance)}
        </span>
      ),
    },
    {
      key: 'explanation',
      label: 'Root Cause & Resolution Guidance',
      render: (row) => (
        <span className="text-xs text-gray-700 max-w-md block" title={row.explanation}>
          {row.explanation}
        </span>
      ),
    },
  ]

  return (
    <div className="space-y-6">
      {/* Page Title */}
      <div className="bg-white p-5 rounded-xl border border-gray-100 shadow-sm">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-red-50 text-red-600 rounded-lg">
            <AlertTriangle size={24} />
          </div>
          <div>
            <h1 className="text-xl font-bold text-gray-900">Exception & Discrepancy Desk</h1>
            <p className="text-xs text-gray-500 mt-1">
              Flagged items requiring finance team review: timing delays, rounding variances, duplicates, and orphan refunds.
            </p>
          </div>
        </div>
      </div>

      {/* Exception Breakdown Cards */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
        <div className="bg-white p-3.5 rounded-xl border border-gray-100 shadow-sm">
          <div className="flex items-center justify-between text-amber-600 mb-1">
            <span className="text-[11px] font-medium text-gray-600">Timing Diffs</span>
            <Clock size={16} />
          </div>
          <div className="text-xl font-bold text-gray-900 font-mono">{counts['TIMING_DIFFERENCE'] || 0}</div>
          <span className="text-[10px] text-gray-400">Next-month settlements</span>
        </div>

        <div className="bg-white p-3.5 rounded-xl border border-gray-100 shadow-sm">
          <div className="flex items-center justify-between text-orange-600 mb-1">
            <span className="text-[11px] font-medium text-gray-600">Rounding</span>
            <Calculator size={16} />
          </div>
          <div className="text-xl font-bold text-gray-900 font-mono">{counts['ROUNDING_DIFFERENCE'] || 0}</div>
          <span className="text-[10px] text-gray-400">Fractional variances</span>
        </div>

        <div className="bg-white p-3.5 rounded-xl border border-gray-100 shadow-sm">
          <div className="flex items-center justify-between text-red-600 mb-1">
            <span className="text-[11px] font-medium text-gray-600">Duplicates</span>
            <Copy size={16} />
          </div>
          <div className="text-xl font-bold text-gray-900 font-mono">{counts['DUPLICATE'] || 0}</div>
          <span className="text-[10px] text-gray-400">Repeated settlements</span>
        </div>

        <div className="bg-white p-3.5 rounded-xl border border-gray-100 shadow-sm">
          <div className="flex items-center justify-between text-red-600 mb-1">
            <span className="text-[11px] font-medium text-gray-600">Orphan Refunds</span>
            <FileX size={16} />
          </div>
          <div className="text-xl font-bold text-gray-900 font-mono">{counts['ORPHAN_REFUND'] || 0}</div>
          <span className="text-[10px] text-gray-400">No original txn found</span>
        </div>

        <div className="bg-white p-3.5 rounded-xl border border-gray-100 shadow-sm">
          <div className="flex items-center justify-between text-red-600 mb-1">
            <span className="text-[11px] font-medium text-gray-600">Missing Settles</span>
            <AlertTriangle size={16} />
          </div>
          <div className="text-xl font-bold text-gray-900 font-mono">{counts['MISSING_SETTLEMENT'] || 0}</div>
          <span className="text-[10px] text-gray-400">Pending bank credit</span>
        </div>

        <div className="bg-white p-3.5 rounded-xl border border-gray-100 shadow-sm">
          <div className="flex items-center justify-between text-purple-600 mb-1">
            <span className="text-[11px] font-medium text-gray-600">Unmatched Stl</span>
            <HelpCircle size={16} />
          </div>
          <div className="text-xl font-bold text-gray-900 font-mono">{counts['UNMATCHED_SETTLEMENT'] || 0}</div>
          <span className="text-[10px] text-gray-400">Bank ref unmapped</span>
        </div>
      </div>

      {/* Exception Table */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
        <DataTable
          columns={columns}
          data={exceptions}
          loading={loading}
          emptyMessage="No discrepancies or exceptions found. Books are balanced!"
          pageSize={10}
        />
      </div>
    </div>
  )
}
