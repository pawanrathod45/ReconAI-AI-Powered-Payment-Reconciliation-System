import { useState, useEffect } from 'react'
import {
  Layers,
  IndianRupee,
  CheckCircle,
  AlertTriangle,
  Percent,
  Clock,
  Calculator,
  Copy,
  FileX,
  Loader2,
  Database,
} from 'lucide-react'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend,
  PieChart, Pie, Cell,
  LineChart, Line,
} from 'recharts'
import MetricCard from '../components/MetricCard'
import ChartCard from '../components/ChartCard'
import { getReconciliationSummary, getReconciliationResults, generateSampleData } from '../services/api'

const PIE_COLORS = ['#10b981', '#f59e0b', '#f97316', '#ef4444', '#ef4444', '#ef4444', '#8b5cf6']

function formatINR(value) {
  if (value == null || value === '') return '₹0.00'
  const num = typeof value === 'string' ? parseFloat(value) : value
  if (isNaN(num)) return '₹0.00'
  return '₹' + num.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

function formatNumber(value) {
  if (value == null) return '0'
  return Number(value).toLocaleString('en-IN')
}

export default function Dashboard() {
  const [summary, setSummary] = useState(null)
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [generating, setGenerating] = useState(false)

  const fetchData = async () => {
    setLoading(true)
    setError(null)
    try {
      const [sumRes, resRes] = await Promise.all([
        getReconciliationSummary(),
        getReconciliationResults().catch(() => ({ data: [] })),
      ])
      setSummary(sumRes.data)
      setResults(Array.isArray(resRes.data) ? resRes.data : [])
    } catch (err) {
      if (err.response?.status === 404) {
        setSummary(null)
      } else {
        setError('Failed to load dashboard data')
      }
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { fetchData() }, [])

  const handleGenerate = async () => {
    setGenerating(true)
    try {
      await generateSampleData()
      await fetchData()
    } catch {
      setError('Failed to generate sample data')
    } finally {
      setGenerating(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 size={32} className="animate-spin text-blue-500" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center h-64 text-center">
        <AlertTriangle size={32} className="text-red-400 mb-2" />
        <p className="text-red-600 font-medium">{error}</p>
        <button onClick={fetchData} className="mt-3 text-sm text-blue-600 hover:underline">
          Try again
        </button>
      </div>
    )
  }

  const isEmpty = !summary || (summary.total_transactions === 0 && summary.total_settlements === 0)

  if (isEmpty) {
    return (
      <div className="flex flex-col items-center justify-center h-64 text-center">
        <Database size={48} className="text-gray-300 mb-3" />
        <h2 className="text-lg font-semibold text-gray-700">No data available</h2>
        <p className="text-sm text-gray-500 mt-1 max-w-md">
          Generate sample data or upload files to get started.
        </p>
        <button
          onClick={handleGenerate}
          disabled={generating}
          className="mt-4 px-5 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 disabled:opacity-60 flex items-center gap-2"
        >
          {generating ? <Loader2 size={16} className="animate-spin" /> : <Database size={16} />}
          {generating ? 'Generating...' : 'Generate Sample Data'}
        </button>
      </div>
    )
  }

  // Build chart data from summary
  const statusPieData = [
    { name: 'Matched', value: summary.matched_count || 0 },
    { name: 'Timing Diff', value: summary.timing_differences || 0 },
    { name: 'Rounding Diff', value: summary.rounding_differences || 0 },
    { name: 'Duplicates', value: summary.duplicates || 0 },
    { name: 'Missing Sett.', value: summary.orphan_refunds || 0 },
    { name: 'Orphan Refunds', value: summary.orphan_refunds || 0 },
    { name: 'Unmatched Sett.', value: summary.unmatched_settlements || 0 },
  ].filter((d) => d.value > 0)

  const amountBarData = [
    {
      name: 'Totals',
      Transactions: parseFloat(summary.total_transaction_amount) || 0,
      Settlements: parseFloat(summary.total_settlement_amount) || 0,
    },
  ]

  // Build daily trends from results
  const dailyMap = {}
  results.forEach((r) => {
    const date = r.reconciliation_date || r.transaction_date
    if (!date) return
    const d = date.slice(0, 10)
    if (!dailyMap[d]) dailyMap[d] = { date: d, count: 0, amount: 0 }
    dailyMap[d].count++
    dailyMap[d].amount += parseFloat(r.transaction_amount || 0)
  })
  const dailyTrends = Object.values(dailyMap).sort((a, b) => a.date.localeCompare(b.date))

  const discrepancyData = [
    { name: 'Timing', value: summary.timing_differences || 0 },
    { name: 'Rounding', value: summary.rounding_differences || 0 },
    { name: 'Duplicates', value: summary.duplicates || 0 },
    { name: 'Orphan Ref.', value: summary.orphan_refunds || 0 },
    { name: 'Unmatched Sett.', value: summary.unmatched_settlements || 0 },
  ]

  const reconRate = summary.reconciliation_rate ?? 0
  const rateColor = reconRate >= 95 ? 'green' : reconRate >= 80 ? 'amber' : 'red'

  return (
    <div className="space-y-6">
      {/* Top metrics row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        <MetricCard icon={Layers} title="Total Transactions" value={formatNumber(summary.total_transactions)} color="blue" />
        <MetricCard icon={IndianRupee} title="Total Amount" value={formatINR(summary.total_transaction_amount)} color="blue" />
        <MetricCard icon={CheckCircle} title="Matched" value={formatNumber(summary.matched_count)} subtitle={`of ${formatNumber(summary.total_transactions)} transactions`} color="green" />
        <MetricCard icon={AlertTriangle} title="Exceptions" value={formatNumber(summary.unmatched_count)} color="red" />
        <MetricCard icon={Percent} title="Reconciliation Rate" value={`${reconRate.toFixed(1)}%`} color={rateColor} />
      </div>

      {/* Second metrics row */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard icon={Clock} title="Timing Differences" value={formatNumber(summary.timing_differences)} color="amber" />
        <MetricCard icon={Calculator} title="Rounding Differences" value={formatNumber(summary.rounding_differences)} color="orange" />
        <MetricCard icon={Copy} title="Duplicates" value={formatNumber(summary.duplicates)} color="red" />
        <MetricCard icon={FileX} title="Orphan Refunds" value={formatNumber(summary.orphan_refunds)} color="red" />
      </div>

      {/* Charts row 1 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ChartCard title="Transaction vs Settlement Amounts" subtitle="Total comparison">
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={amountBarData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="name" tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 12 }} tickFormatter={(v) => `₹${(v / 1000).toFixed(0)}k`} />
              <Tooltip formatter={(v) => formatINR(v)} />
              <Legend />
              <Bar dataKey="Transactions" fill="#3b82f6" radius={[4, 4, 0, 0]} />
              <Bar dataKey="Settlements" fill="#10b981" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard title="Reconciliation Status Distribution" subtitle="Breakdown by category">
          <ResponsiveContainer width="100%" height={260}>
            <PieChart>
              <Pie
                data={statusPieData}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={100}
                dataKey="value"
                paddingAngle={2}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
              >
                {statusPieData.map((_, i) => (
                  <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>

      {/* Charts row 2 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ChartCard title="Daily Transaction Trends" subtitle="Transaction volume over time">
          <ResponsiveContainer width="100%" height={260}>
            <LineChart data={dailyTrends}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="date" tick={{ fontSize: 10 }} />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="count" name="Transactions" stroke="#3b82f6" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard title="Discrepancy Category Distribution" subtitle="Exception types breakdown">
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={discrepancyData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="name" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip />
              <Bar dataKey="value" name="Count" fill="#f59e0b" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>
    </div>
  )
}
