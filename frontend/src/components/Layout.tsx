import { ReactNode } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { Shield, Activity, AlertTriangle, FileText, Code, History } from 'lucide-react'

interface LayoutProps {
  children: ReactNode
}

const navigation = [
  { name: 'Dashboard', href: '/', icon: Activity },
  { name: 'Monitoring', href: '/monitoring', icon: Shield },
  { name: 'Risk Scoring', href: '/risk', icon: AlertTriangle },
  { name: 'Reporting', href: '/reporting', icon: FileText },
  { name: 'Smart Contracts', href: '/contracts', icon: Code },
  { name: 'Audit Trail', href: '/audit', icon: History },
]

export default function Layout({ children }: LayoutProps) {
  const location = useLocation()

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Sidebar */}
      <div className="fixed inset-y-0 left-0 w-64 bg-gray-900">
        <div className="flex h-16 items-center justify-center border-b border-gray-800">
          <h1 className="text-xl font-bold text-white">Compliance Monitor</h1>
        </div>
        <nav className="mt-6 px-3">
          {navigation.map((item) => {
            const isActive = location.pathname === item.href
            const Icon = item.icon
            return (
              <Link
                key={item.name}
                to={item.href}
                className={`
                  flex items-center gap-3 rounded-lg px-3 py-2 mb-1
                  transition-colors duration-200
                  ${
                    isActive
                      ? 'bg-primary-600 text-white'
                      : 'text-gray-300 hover:bg-gray-800 hover:text-white'
                  }
                `}
              >
                <Icon size={20} />
                <span className="font-medium">{item.name}</span>
              </Link>
            )
          })}
        </nav>
      </div>

      {/* Main content */}
      <div className="pl-64">
        {/* Top bar */}
        <header className="bg-white shadow-sm h-16 flex items-center justify-between px-8">
          <h2 className="text-2xl font-semibold text-gray-900">
            Global Settlement
          </h2>
          <div className="flex items-center gap-4">
            <div className="text-sm text-gray-600">
              Last updated: {new Date().toLocaleTimeString()}
            </div>
            <div className="h-2 w-2 rounded-full bg-green-500" />
          </div>
        </header>

        {/* Page content */}
        <main className="p-8">{children}</main>
      </div>
    </div>
  )
}
