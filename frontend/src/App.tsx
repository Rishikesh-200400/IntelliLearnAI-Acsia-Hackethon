import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { useEffect, useState } from 'react'
import Layout from './components/Layout'
import Home from './pages/Home'
import Employees from './pages/Employees'
import EmployeeDetail from './pages/EmployeeDetail'
import Recommendations from './pages/Recommendations'
import Analytics from './pages/Analytics'
import Admin from './pages/Admin'
import AdminLogin from './pages/AdminLogin'
import Login from './pages/Login'
import MyAnalytics from './pages/MyAnalytics'
import EmployeeDashboard from './pages/employee/Dashboard'
import CourseDetail from './pages/CourseDetail'
import Assessment from './pages/Assessment'
import SkillGapAnalysis from './pages/SkillGapAnalysis'
import ROIDashboard from './pages/ROIDashboard'
import LearningPath from './pages/LearningPath'
import SkillComparison from './pages/SkillComparison'
import CourseCatalog from './pages/CourseCatalog'
import { Navigate } from 'react-router-dom'
import { ToastProvider } from './components/ui/toast'

function RequireAdmin({ children }: { children: JSX.Element }) {
  const token = typeof window !== 'undefined' ? localStorage.getItem('auth_token') : null
  const role = typeof window !== 'undefined' ? localStorage.getItem('role') : null
  if (!token || role !== 'admin') {
    return <Navigate to="/admin/login" replace />
  }
  return children
}

function RequireEmployee({ children }: { children: JSX.Element }) {
  const token = typeof window !== 'undefined' ? localStorage.getItem('auth_token') : null
  const employeeId = typeof window !== 'undefined' ? localStorage.getItem('employee_id') : null
  const role = typeof window !== 'undefined' ? localStorage.getItem('role') : null
  if (!token || !employeeId || role !== 'employee') {
    return <Navigate to="/login" replace />
  }
  return children
}

function App() {
  const [authReady, setAuthReady] = useState(false)

  useEffect(() => {
    const token = localStorage.getItem('auth_token')
    const storedRole = localStorage.getItem('role')
    if (!token) {
      setAuthReady(true)
      return
    }
    if (storedRole) {
      setAuthReady(true)
      return
    }
    // Try to restore role/employee from backend
    import('./lib/api').then(({ default: api }) => {
      api.get('/api/auth/me')
        .then(res => {
          if (res.data?.role) localStorage.setItem('role', res.data.role)
          if (res.data?.employee_id) localStorage.setItem('employee_id', String(res.data.employee_id))
        })
        .catch(() => {})
        .finally(() => setAuthReady(true))
    })
  }, [])

  if (!authReady) {
    return <div className="min-h-screen flex items-center justify-center">Loading...</div>
  }

  function HomeGate() {
    const token = typeof window !== 'undefined' ? localStorage.getItem('auth_token') : null
    const role = typeof window !== 'undefined' ? localStorage.getItem('role') : null
    if (token && role === 'admin') return <Navigate to="/admin" replace />
    if (token && role === 'employee') return <Navigate to="/my-analytics" replace />
    return <Home />
  }

  return (
    <ToastProvider>
      <Router>
        <Layout>
          <Routes>
            <Route path="/" element={<HomeGate />} />
            <Route path="/login" element={<Login />} />
            <Route path="/employees" element={<Employees />} />
            <Route path="/employees/:id" element={<EmployeeDetail />} />
            <Route path="/recommendations" element={<RequireEmployee><Recommendations /></RequireEmployee>} />
            <Route path="/employee/dashboard" element={<RequireEmployee><EmployeeDashboard /></RequireEmployee>} />
            <Route path="/my-analytics" element={<RequireEmployee><MyAnalytics /></RequireEmployee>} />
            <Route path="/course/:trainingId" element={<RequireEmployee><CourseDetail /></RequireEmployee>} />
            <Route path="/assessment/:trainingId" element={<RequireEmployee><Assessment /></RequireEmployee>} />
            <Route path="/analytics" element={<Analytics />} />
            <Route path="/skill-gap-analysis" element={<RequireAdmin><SkillGapAnalysis /></RequireAdmin>} />
            <Route path="/roi-dashboard" element={<RequireAdmin><ROIDashboard /></RequireAdmin>} />
            <Route path="/learning-path" element={<RequireEmployee><LearningPath /></RequireEmployee>} />
            <Route path="/skill-comparison" element={<RequireEmployee><SkillComparison /></RequireEmployee>} />
            <Route path="/course-catalog" element={<CourseCatalog />} />
            <Route path="/admin/login" element={<AdminLogin />} />
            <Route path="/admin" element={<RequireAdmin><Admin /></RequireAdmin>} />
          </Routes>
        </Layout>
      </Router>
    </ToastProvider>
  )
}

export default App
