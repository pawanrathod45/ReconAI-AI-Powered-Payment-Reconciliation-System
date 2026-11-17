import { useState } from 'react'
import { FileText, FileSpreadsheet, Download, CheckCircle, AlertCircle, Loader2 } from 'lucide-react'
import { exportReport } from '../services/api'

export default function Reports() {
  const [downloading, setDownloading] = useState(null)
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(null)

  const handleDownload = async (format, type, filename) => {
    const key = `${format}_${type}`
    setDownloading(key)
    setError(null)
    setSuccess(null)

    try {
      const res = await exportReport(format, type)
      const blob = new Blob([res.data], {
        type: format === 'pdf' ? 'application/pdf' : 'text/csv',
      })
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', filename)
      document.body.appendChild(link)
      link.click()
      link.parentNode.removeChild(link)
      window.URL.revokeObjectURL(url)
      setSuccess(`Downloaded ${filename} successfully!`)
    } catch (err) {
      setError(`Failed to download ${filename}. Verify reconciliation has been run.`)
    } finally {
      setDownloading(null)
    }
  }

  const reports = [
    {
      title: 'Full Reconciliation Ledger',
      description: 'Comprehensive audit report containing all processed transactions, matching statuses, variances, and explanations.',
      format: 'csv',
      type: 'full',
      filename: 'reconai_full_reconciliation_report.csv',
      icon: FileSpreadsheet,
      badge: 'CSV',
      badgeColor: 'bg-emerald-100 text-emerald-800',
    },
    {
      title: 'Exception & Discrepancy Report',
      description: 'Targeted report detailing timing differences, rounding gaps, duplicate entries, and orphan refunds for immediate investigation.',
      format: 'csv',
      type: 'exceptions',
      filename: 'reconai_exceptions_report.csv',
      icon: FileSpreadsheet,
      badge: 'CSV',
      badgeColor: 'bg-amber-100 text-amber-800',
    },
    {
      title: 'Monthly Financial Summary',
      description: 'Executive month-end summary with opening balances, gross inflows, timing deferrals, resolved sums, and closing status.',
      format: 'csv',
      type: 'monthly',
      filename: 'reconai_monthly_summary.csv',
      icon: FileSpreadsheet,
      badge: 'CSV',
      badgeColor: 'bg-blue-100 text-blue-800',
    },
    {
      title: 'Formal Audit Report (PDF)',
      description: 'Printable executive-ready PDF report formatted with executive overview, discrepancy category analysis, and key findings.',
      format: 'pdf',
      type: 'full',
      filename: 'reconai_audit_report.pdf',
      icon: FileText,
      badge: 'PDF',
      badgeColor: 'bg-red-100 text-red-800',
    },
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white p-5 rounded-xl border border-gray-100 shadow-sm">
        <h1 className="text-xl font-bold text-gray-900">Audit & Compliance Reports</h1>
        <p className="text-xs text-gray-500 mt-1">
          Export verified reconciliation statements for statutory audits, bank correspondence, and internal finance sign-off.
        </p>
      </div>

      {success && (
        <div className="flex items-center gap-2 p-3 bg-emerald-50 border border-emerald-200 text-emerald-800 rounded-lg text-xs font-medium">
          <CheckCircle size={16} className="text-emerald-600 flex-shrink-0" />
          <span>{success}</span>
        </div>
      )}

      {error && (
        <div className="flex items-center gap-2 p-3 bg-red-50 border border-red-200 text-red-800 rounded-lg text-xs font-medium">
          <AlertCircle size={16} className="text-red-600 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Grid of Report Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {reports.map((report) => {
          const Icon = report.icon
          const key = `${report.format}_${report.type}`
          const isDownloading = downloading === key

          return (
            <div
              key={key}
              className="bg-white p-5 rounded-xl border border-gray-100 shadow-sm flex flex-col justify-between hover:shadow-md transition-shadow"
            >
              <div>
                <div className="flex items-center justify-between mb-3">
                  <div className="p-2.5 bg-gray-50 text-slate-800 rounded-lg border border-gray-100">
                    <Icon size={22} />
                  </div>
                  <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full uppercase tracking-wider ${report.badgeColor}`}>
                    {report.badge}
                  </span>
                </div>
                <h3 className="text-sm font-bold text-gray-900">{report.title}</h3>
                <p className="text-xs text-gray-500 mt-1.5 leading-relaxed">{report.description}</p>
              </div>

              <div className="mt-5 pt-4 border-t border-gray-100 flex items-center justify-between">
                <span className="text-[11px] font-mono text-gray-400">{report.filename}</span>
                <button
                  onClick={() => handleDownload(report.format, report.type, report.filename)}
                  disabled={isDownloading}
                  className="flex items-center gap-1.5 px-3.5 py-1.5 bg-slate-900 hover:bg-slate-800 text-white text-xs font-semibold rounded-lg shadow-sm transition-colors disabled:opacity-50"
                >
                  {isDownloading ? (
                    <>
                      <Loader2 size={13} className="animate-spin" />
                      <span>Generating...</span>
                    </>
                  ) : (
                    <>
                      <Download size={13} />
                      <span>Export</span>
                    </>
                  )}
                </button>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
