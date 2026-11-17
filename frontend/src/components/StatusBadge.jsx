const statusConfig = {
  MATCHED: {
    label: 'Matched',
    bg: 'bg-emerald-50',
    text: 'text-emerald-700',
    ring: 'ring-emerald-600/20',
  },
  TIMING_DIFFERENCE: {
    label: 'Timing Diff',
    bg: 'bg-amber-50',
    text: 'text-amber-700',
    ring: 'ring-amber-600/20',
  },
  ROUNDING_DIFFERENCE: {
    label: 'Rounding Diff',
    bg: 'bg-orange-50',
    text: 'text-orange-700',
    ring: 'ring-orange-600/20',
  },
  DUPLICATE: {
    label: 'Duplicate',
    bg: 'bg-red-50',
    text: 'text-red-700',
    ring: 'ring-red-600/20',
  },
  MISSING_SETTLEMENT: {
    label: 'Missing Settlement',
    bg: 'bg-red-50',
    text: 'text-red-700',
    ring: 'ring-red-600/20',
  },
  ORPHAN_REFUND: {
    label: 'Orphan Refund',
    bg: 'bg-red-50',
    text: 'text-red-700',
    ring: 'ring-red-600/20',
  },
  UNMATCHED_SETTLEMENT: {
    label: 'Unmatched Settlement',
    bg: 'bg-purple-50',
    text: 'text-purple-700',
    ring: 'ring-purple-600/20',
  },
}

export default function StatusBadge({ status }) {
  const config = statusConfig[status] || {
    label: status,
    bg: 'bg-gray-50',
    text: 'text-gray-700',
    ring: 'ring-gray-600/20',
  }

  return (
    <span
      className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ring-1 ring-inset ${config.bg} ${config.text} ${config.ring}`}
    >
      {config.label}
    </span>
  )
}
