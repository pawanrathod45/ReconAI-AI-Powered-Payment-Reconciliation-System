import { useState } from 'react'
import { Database, Download, Loader2 } from 'lucide-react'
import FileUpload from '../components/FileUpload'
import { uploadTransactions, uploadSettlements, generateSampleData } from '../services/api'

export default function Upload() {
  const [txnUploading, setTxnUploading] = useState(false)
  const [setUploading, setSetUploading] = useState(false)
  const [txnResult, setTxnResult] = useState(null)
  const [setResult, setSetResult] = useState(null)
  const [generating, setGenerating] = useState(false)
  const [genResult, setGenResult] = useState(null)

  const handleTxnUpload = async (file) => {
    setTxnUploading(true)
    setTxnResult(null)
    try {
      const res = await uploadTransactions(file)
      setTxnResult({ success: true, message: `Successfully uploaded ${res.data.count} transactions`, errors: [] })
    } catch (err) {
      const data = err.response?.data
      setTxnResult({
        success: false,
        message: data?.message || 'Upload failed',
        errors: data?.errors || [err.message],
      })
    } finally {
      setTxnUploading(false)
    }
  }

  const handleSetUpload = async (file) => {
    setSetUploading(true)
    setSetResult(null)
    try {
      const res = await uploadSettlements(file)
      setSetResult({ success: true, message: `Successfully uploaded ${res.data.count} settlements`, errors: [] })
    } catch (err) {
      const data = err.response?.data
      setSetResult({
        success: false,
        message: data?.message || 'Upload failed',
        errors: data?.errors || [err.message],
      })
    } finally {
      setSetUploading(false)
    }
  }

  const handleGenerate = async () => {
    setGenerating(true)
    setGenResult(null)
    try {
      const res = await generateSampleData()
      setGenResult({
        success: true,
        message: `Generated ${res.data.transaction_count} transactions and ${res.data.settlement_count} settlements`,
      })
    } catch (err) {
      setGenResult({ success: false, message: err.response?.data?.message || 'Generation failed' })
    } finally {
      setGenerating(false)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-gray-900">Upload Data</h2>
        <p className="text-sm text-gray-500 mt-1">
          Upload transaction and settlement CSV files to begin reconciliation.
        </p>
      </div>

      {/* Upload panels */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <FileUpload
          label="Transaction CSV"
          onUpload={handleTxnUpload}
          uploading={txnUploading}
          result={txnResult}
        />
        <FileUpload
          label="Settlement CSV"
          onUpload={handleSetUpload}
          uploading={setUploading}
          result={setResult}
        />
      </div>

      {/* Sample data section */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div>
            <h3 className="text-sm font-semibold text-gray-900">Or Generate Sample Data</h3>
            <p className="text-xs text-gray-500 mt-0.5">
              Create realistic sample transactions and settlements for testing.
            </p>
          </div>
          <button
            onClick={handleGenerate}
            disabled={generating}
            className="px-5 py-2 bg-slate-800 text-white text-sm font-medium rounded-lg hover:bg-slate-900 disabled:opacity-60 flex items-center gap-2 shrink-0"
          >
            {generating ? <Loader2 size={16} className="animate-spin" /> : <Database size={16} />}
            {generating ? 'Generating...' : 'Generate Sample Data'}
          </button>
        </div>

        {genResult && (
          <div
            className={`mt-3 rounded-lg px-3 py-2 text-sm ${
              genResult.success ? 'bg-emerald-50 text-emerald-700' : 'bg-red-50 text-red-700'
            }`}
          >
            {genResult.message}
          </div>
        )}
      </div>

      {/* Template download links */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
        <h3 className="text-sm font-semibold text-gray-900 mb-3">CSV Templates</h3>
        <p className="text-xs text-gray-500 mb-3">
          Download sample CSV templates to understand the expected format.
        </p>
        <div className="flex flex-wrap gap-3">
          <a
            href="/api/reports/export?format=csv&type=transactions_template"
            className="inline-flex items-center gap-1.5 px-3 py-1.5 text-sm text-blue-600 bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors"
          >
            <Download size={14} />
            Transaction Template
          </a>
          <a
            href="/api/reports/export?format=csv&type=settlements_template"
            className="inline-flex items-center gap-1.5 px-3 py-1.5 text-sm text-blue-600 bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors"
          >
            <Download size={14} />
            Settlement Template
          </a>
        </div>
      </div>
    </div>
  )
}
