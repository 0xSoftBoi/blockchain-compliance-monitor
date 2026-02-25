import { useQuery } from '@tanstack/react-query'
import { AlertCircle, CheckCircle, TrendingUp, Shield } from 'lucide-react'

interface Stats {
  activeAlerts: number
  transactionsMonitored: number
  complianceScore: number
  highRiskEntities: number
}

export default function Dashboard() {
  const { data: stats } = useQuery<Stats>({
    queryKey: ['dashboard-stats'],
    queryFn: async () => {
      // In production, fetch from API
      return {
        activeAlerts: 12,
        transactionsMonitored: 15847,
        complianceScore: 94,
        highRiskEntities: 23,
      }
    },
  })

  const statCards = [
    {
      title: 'Active Alerts',
      value: stats?.activeAlerts ?? 0,
      icon: AlertCircle,
      color: 'text-warning-600',
      bgColor: 'bg-warning-50',
    },
    {
      title: 'Transactions Monitored',
      value: stats?.transactionsMonitored.toLocaleString() ?? '0',
      icon: TrendingUp,
      color: 'text-primary-600',
      bgColor: 'bg-primary-50',
    },
    {
      title: 'Compliance Score',
      value: `${stats?.complianceScore ?? 0}%`,
      icon: CheckCircle,
      color: 'text-success-600',
      bgColor: 'bg-success-50',
    },
    {
      title: 'High Risk Entities',
      value: stats?.highRiskEntities ?? 0,
      icon: Shield,
      color: 'text-danger-600',
      bgColor: 'bg-danger-50',
    },
  ]

  return (
    <div>
      <h1 className="text-3xl font-bold text-gray-900 mb-8">
        Compliance Dashboard
      </h1>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {statCards.map((stat) => {
          const Icon = stat.icon
          return (
            <div
              key={stat.title}
              className="bg-white rounded-lg shadow-sm p-6 border border-gray-200"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">
                    {stat.title}
                  </p>
                  <p className="text-2xl font-bold text-gray-900 mt-2">
                    {stat.value}
                  </p>
                </div>
                <div className={`${stat.bgColor} ${stat.color} p-3 rounded-lg`}>
                  <Icon size={24} />
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {/* Recent Alerts */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">
          Recent Compliance Alerts
        </h2>
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <div
              key={i}
              className="flex items-center justify-between py-3 border-b border-gray-100 last:border-0"
            >
              <div className="flex items-center gap-3">
                <div className="h-2 w-2 rounded-full bg-warning-500" />
                <div>
                  <p className="font-medium text-gray-900">
                    High-value transaction detected
                  </p>
                  <p className="text-sm text-gray-500">
                    0x742d...ef8a • $45,000 USD
                  </p>
                </div>
              </div>
              <span className="text-sm text-gray-500">
                {new Date().toLocaleTimeString()}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
