import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Monitoring from './pages/Monitoring'
import RiskScoring from './pages/RiskScoring'
import Reporting from './pages/Reporting'
import SmartContracts from './pages/SmartContracts'
import AuditTrail from './pages/AuditTrail'

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/monitoring" element={<Monitoring />} />
          <Route path="/risk" element={<RiskScoring />} />
          <Route path="/reporting" element={<Reporting />} />
          <Route path="/contracts" element={<SmartContracts />} />
          <Route path="/audit" element={<AuditTrail />} />
        </Routes>
      </Layout>
    </Router>
  )
}

export default App
