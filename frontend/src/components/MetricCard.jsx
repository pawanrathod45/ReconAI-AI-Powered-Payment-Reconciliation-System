export default function MetricCard({ icon: Icon, title, value, subtitle, color = 'blue', className = '' }) {
  const colorMap = {
    blue: {
      bg: 'bg-blue-50',
      icon: 'text-blue-600',
      ring: 'ring-blue-100',
    },
    green: {
      bg: 'bg-emerald-50',
      icon: 'text-emerald-600',
      ring: 'ring-emerald-100',
    },
    amber: {
      bg: 'bg-amber-50',
      icon: 'text-amber-600',
      ring: 'ring-amber-100',
    },
    orange: {
      bg: 'bg-orange-50',
      icon: 'text-orange-600',
      ring: 'ring-orange-100',
    },
    red: {
      bg: 'bg-red-50',
      icon: 'text-red-600',
      ring: 'ring-red-100',
    },
    purple: {
      bg: 'bg-purple-50',
      icon: 'text-purple-600',
      ring: 'ring-purple-100',
    },
  }

  const colors = colorMap[color] || colorMap.blue

  return (
    <div className={`bg-white rounded-xl shadow-sm border border-gray-100 p-4 lg:p-5 ${className}`}>
      <div className="flex items-start justify-between">
        <div className="flex-1 min-w-0">
          <p className="text-sm text-gray-500 font-medium truncate">{title}</p>
          <p className="mt-1.5 text-2xl font-bold text-gray-900 font-mono truncate">{value}</p>
          {subtitle && (
            <p className="mt-1 text-xs text-gray-400">{subtitle}</p>
          )}
        </div>
        <div className={`ml-3 p-2.5 rounded-lg ${colors.bg} ring-1 ${colors.ring} shrink-0`}>
          <Icon size={20} className={colors.icon} />
        </div>
      </div>
    </div>
  )
}
