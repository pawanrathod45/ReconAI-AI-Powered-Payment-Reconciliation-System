import { useState, useRef, useCallback } from 'react'
import { Upload, FileUp, CheckCircle, XCircle, Loader2 } from 'lucide-react'

export default function FileUpload({ label, accept = '.csv', onUpload, uploading = false, result = null }) {
  const [file, setFile] = useState(null)
  const [dragOver, setDragOver] = useState(false)
  const inputRef = useRef(null)

  const handleDrop = useCallback((e) => {
    e.preventDefault()
    setDragOver(false)
    const dropped = e.dataTransfer.files[0]
    if (dropped) setFile(dropped)
  }, [])

  const handleDragOver = useCallback((e) => {
    e.preventDefault()
    setDragOver(true)
  }, [])

  const handleDragLeave = useCallback(() => {
    setDragOver(false)
  }, [])

  const handleSelect = (e) => {
    const selected = e.target.files[0]
    if (selected) setFile(selected)
  }

  const handleUpload = () => {
    if (file && onUpload) {
      onUpload(file)
    }
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
      <h3 className="text-sm font-semibold text-gray-900 mb-3">{label}</h3>

      <div
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onClick={() => inputRef.current?.click()}
        className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
          dragOver
            ? 'border-blue-400 bg-blue-50'
            : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
        }`}
      >
        <input
          ref={inputRef}
          type="file"
          accept={accept}
          onChange={handleSelect}
          className="hidden"
        />
        <FileUp size={32} className="mx-auto text-gray-400 mb-2" />
        <p className="text-sm text-gray-600">
          <span className="text-blue-600 font-medium">Click to upload</span> or drag & drop
        </p>
        <p className="text-xs text-gray-400 mt-1">CSV files only</p>
      </div>

      {file && (
        <div className="mt-3 flex items-center justify-between bg-gray-50 rounded-lg px-3 py-2">
          <span className="text-sm text-gray-700 truncate">{file.name}</span>
          <button
            onClick={handleUpload}
            disabled={uploading}
            className="ml-3 px-4 py-1.5 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 disabled:opacity-60 flex items-center gap-1.5 shrink-0"
          >
            {uploading ? (
              <>
                <Loader2 size={14} className="animate-spin" />
                Uploading...
              </>
            ) : (
              <>
                <Upload size={14} />
                Upload
              </>
            )}
          </button>
        </div>
      )}

      {result && (
        <div
          className={`mt-3 flex items-start gap-2 rounded-lg px-3 py-2 text-sm ${
            result.success
              ? 'bg-emerald-50 text-emerald-700'
              : 'bg-red-50 text-red-700'
          }`}
        >
          {result.success ? <CheckCircle size={16} className="mt-0.5 shrink-0" /> : <XCircle size={16} className="mt-0.5 shrink-0" />}
          <div>
            <p className="font-medium">{result.message}</p>
            {result.errors && result.errors.length > 0 && (
              <ul className="mt-1 text-xs list-disc list-inside">
                {result.errors.map((err, i) => <li key={i}>{err}</li>)}
              </ul>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
