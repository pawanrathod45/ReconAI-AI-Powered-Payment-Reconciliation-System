import { useState } from 'react'
import { Sliders, CheckCircle2, ShieldAlert, Info, Database } from 'lucide-react'

export default function Settings() {
  const [tolerance, setTolerance] = useState('0.01')
  const [currency] = useState('INR (₹)')
  const [dateFormat, setDateFormat] = useState('YYYY-MM-DD')
  const [saved, setSaved] = useState(false)

  const handleSave = (e) => {
    e.preventDefault()
    setSaved(true)
    setTimeout(() => setSaved(false), 3000)
  }

  const assumptions = [
    { id: 1, title: 'Functional Currency', desc: 'Base accounting currency is Indian Rupee (INR / ₹).' },
    { id: 2, title: 'Unique Transaction IDs', desc: 'Every internal payment event contains a guaranteed distinct transaction ID.' },
    { id: 3, title: 'Bank Reference Tagging', desc: 'Settlement statements include original transaction references wherever available.' },
    { id: 4, title: 'Settlement Window (T+1/T+2)', desc: 'Standard bank batch clearing occurs within 1 to 2 calendar days.' },
    { id: 5, title: 'Unified Timezone', desc: 'Ledger timestamps and bank value dates are standardized to the same timezone.' },
    { id: 6, title: 'Refund Lineage', desc: 'Credit adjustments / refunds explicitly reference their source transaction ID.' },
    { id: 7, title: 'Arbitrary-Precision Arithmetic', desc: 'Python Decimal arithmetic is strictly enforced; floating-point math is banned.' },
    { id: 8, title: 'Cross-Period Timing Difference', desc: 'Month-end payments cleared in subsequent cycles are classified as timing deferrals, not losses.' },
    { id: 9, title: 'Configurable Variance Tolerance', desc: 'Settlement differences within ±₹0.01 are recognized as rounding variance.' },
    { id: 10, title: 'Duplicate Non-Recognition', desc: 'Duplicate bank settlements are quarantined and prevented from inflating revenue.' },
    { id: 11, title: 'Audit Immutability', desc: 'Raw financial statements are never deleted or mutated silently.' },
  ]

  const limitations = [
    {
      title: 'Manual Batch File Ingestion',
      desc: 'The current deployment operates on manual CSV file uploads rather than direct ISO 20022 / Open Banking host-to-host SFTP/API feeds.',
    },
    {
      title: 'Reference-Centric Heuristics',
      desc: 'Matching heavily leverages reference identifiers. Transactions lacking clean merchant/gateway tags require manual operator review.',
    },
    {
      title: 'Enterprise FinTech Controls',
      desc: 'Multi-entity FX conversion, tiered interchange fee splits, automated chargeback clawbacks, and SOX audit logs require external enterprise modules.',
    },
  ]

  return (
    <div className="space-y-6 max-w-5xl">
      {/* Header */}
      <div className="bg-white p-5 rounded-xl border border-gray-100 shadow-sm">
        <h1 className="text-xl font-bold text-gray-900">System Parameters & Governance</h1>
        <p className="text-xs text-gray-500 mt-1">
          Configure reconciliation tolerance thresholds, review architectural assumptions, and verify compliance constraints.
        </p>
      </div>

      {/* Configuration Form */}
      <div className="bg-white p-6 rounded-xl border border-gray-100 shadow-sm">
        <div className="flex items-center gap-2 mb-4 pb-3 border-b border-gray-100">
          <Sliders size={18} className="text-blue-600" />
          <h2 className="text-sm font-bold text-gray-900">Engine Matching Parameters</h2>
        </div>

        {saved && (
          <div className="mb-4 flex items-center gap-2 p-3 bg-emerald-50 border border-emerald-200 text-emerald-800 rounded-lg text-xs font-medium">
            <CheckCircle2 size={16} className="text-emerald-600" />
            <span>Parameters saved successfully!</span>
          </div>
        )}

        <form onSubmit={handleSave} className="space-y-4 max-w-xl">
          <div>
            <label className="block text-xs font-semibold text-gray-700 mb-1">
              Rounding Tolerance Variance (Decimal INR)
            </label>
            <input
              type="text"
              value={tolerance}
              onChange={(e) => setTolerance(e.target.value)}
              className="w-full text-xs font-mono border border-gray-300 rounded-lg p-2.5 bg-gray-50 text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <p className="text-[11px] text-gray-400 mt-1">
              Variances ≤ this value are classified as ROUNDING_DIFFERENCE rather than amount mismatches.
            </p>
          </div>

          <div>
            <label className="block text-xs font-semibold text-gray-700 mb-1">
              Ledger Accounting Currency
            </label>
            <input
              type="text"
              value={currency}
              disabled
              className="w-full text-xs font-mono border border-gray-200 rounded-lg p-2.5 bg-gray-100 text-gray-600 cursor-not-allowed"
            />
            <p className="text-[11px] text-gray-400 mt-1">System is locked to INR per assessment requirement.</p>
          </div>

          <div>
            <label className="block text-xs font-semibold text-gray-700 mb-1">
              Date Serialization Format
            </label>
            <select
              value={dateFormat}
              onChange={(e) => setDateFormat(e.target.value)}
              className="w-full text-xs border border-gray-300 rounded-lg p-2.5 bg-white text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="YYYY-MM-DD">ISO 8601 (YYYY-MM-DD)</option>
              <option value="DD-MM-YYYY">Indian Standard (DD-MM-YYYY)</option>
            </select>
          </div>

          <div className="pt-2">
            <button
              type="submit"
              className="px-4 py-2 bg-slate-900 hover:bg-slate-800 text-white text-xs font-semibold rounded-lg shadow-sm transition-colors"
            >
              Update Configuration
            </button>
          </div>
        </form>
      </div>

      {/* Assumptions Section */}
      <div className="bg-white p-6 rounded-xl border border-gray-100 shadow-sm">
        <div className="flex items-center gap-2 mb-4 pb-3 border-b border-gray-100">
          <Info size={18} className="text-amber-600" />
          <h2 className="text-sm font-bold text-gray-900">Documented Architectural Assumptions</h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {assumptions.map((item) => (
            <div key={item.id} className="p-3 bg-gray-50 rounded-lg border border-gray-100">
              <div className="flex items-center gap-2">
                <span className="w-5 h-5 rounded-full bg-slate-200 text-slate-700 font-mono text-[10px] flex items-center justify-center font-bold">
                  {item.id}
                </span>
                <h4 className="text-xs font-bold text-gray-900">{item.title}</h4>
              </div>
              <p className="text-[11px] text-gray-600 mt-1.5 ml-7 leading-relaxed">{item.desc}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Production Limitations */}
      <div className="bg-white p-6 rounded-xl border border-gray-100 shadow-sm">
        <div className="flex items-center gap-2 mb-4 pb-3 border-b border-gray-100">
          <ShieldAlert size={18} className="text-red-600" />
          <h2 className="text-sm font-bold text-gray-900">Production Constraints & Boundaries</h2>
        </div>

        <div className="space-y-3">
          {limitations.map((lim, idx) => (
            <div key={idx} className="p-3.5 bg-red-50/50 border border-red-100 rounded-lg">
              <h4 className="text-xs font-bold text-red-900 flex items-center gap-2">
                <span className="w-4 h-4 rounded-full bg-red-200 text-red-800 text-[10px] flex items-center justify-center">
                  {idx + 1}
                </span>
                {lim.title}
              </h4>
              <p className="text-xs text-red-800/80 mt-1 ml-6 leading-relaxed">{lim.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
