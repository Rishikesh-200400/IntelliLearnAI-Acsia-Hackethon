import { useEffect, useState } from 'react'
import { BarChart3, TrendingUp, DollarSign, Zap } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { getWorkforceReadiness, getTrainingROI, getDepartmentComparison } from '@/lib/api'
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { useScrollReveal } from '@/hooks/useScrollReveal'

const COLORS = ['#10b981', '#f59e0b', '#ef4444']

export default function Analytics() {
  const [readiness, setReadiness] = useState<any>(null)
  const [roi, setRoi] = useState<any>(null)
  const [departments, setDepartments] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [loadingProgress, setLoadingProgress] = useState('Initializing...')

  // Hooks must be called before any conditional returns
  const ref1 = useScrollReveal()
  const ref2 = useScrollReveal()
  const ref3 = useScrollReveal()

  useEffect(() => {
    let timeout: NodeJS.Timeout;
    
    const fetchData = async () => {
      await loadAnalytics();
      // Clear any pending timeout since we've successfully loaded data
      if (timeout) clearTimeout(timeout);
    };
    
    fetchData();
    
    // Set a timeout to catch stuck loading states
    timeout = setTimeout(() => {
      if (loading) {
        console.warn('[Analytics] Loading took longer than 10 seconds, might be stuck');
        setError('Request timeout - Backend might be slow or unresponsive');
        setLoading(false);
      }
    }, 10000); // 10 second timeout
    
    return () => {
      if (timeout) clearTimeout(timeout);
    };
  }, [])

  const loadAnalytics = async () => {
    const startTime = Date.now()
    console.log('[Analytics] Starting to load analytics data...')
    setError(null)
    setLoadingProgress('Connecting to server...')
    
    try {
      // Add timeout to each request
      const timeoutDuration = 15000 // 15 seconds per request
      
      const requestWithTimeout = async (promiseFn: () => Promise<any>, name: string) => {
        console.log(`[Analytics] Starting ${name} request...`)
        setLoadingProgress(`Loading ${name} data...`)
        
        const controller = new AbortController()
        const timeoutId = setTimeout(() => controller.abort(), timeoutDuration)
        
        try {
          const response = await promiseFn()
          clearTimeout(timeoutId)
          console.log(`[Analytics] ${name} data loaded in ${Date.now() - startTime}ms`)
          return { status: 'fulfilled', value: response }
        } catch (error) {
          clearTimeout(timeoutId)
          console.error(`[Analytics] Error loading ${name}:`, error)
          return { status: 'rejected', reason: error }
        }
      }
      
      // Make all requests in parallel
      const [readinessRes, roiRes, deptRes] = await Promise.all([
        requestWithTimeout(getWorkforceReadiness, 'workforce readiness'),
        requestWithTimeout(() => getTrainingROI(90), 'training ROI'),
        requestWithTimeout(getDepartmentComparison, 'department comparison')
      ])
      
      const loadTime = Date.now() - startTime
      console.log(`[Analytics] All data loaded in ${loadTime}ms`)
      console.log('[Analytics] Readiness data:', readinessRes?.value?.data || 'No data')
      console.log('[Analytics] ROI data:', roiRes?.value?.data || 'No data')
      console.log('[Analytics] Departments data:', Array.isArray(deptRes?.value?.data) ? `${deptRes.value.data.length} departments` : 'No data')
      
      // Process responses
      const errors: string[] = []
      let hasData = false
      
      // Process workforce readiness
      if (readinessRes.status === 'fulfilled' && readinessRes.value?.data) {
        setReadiness(readinessRes.value.data)
        hasData = true
      } else {
        errors.push('Failed to load workforce readiness data')
      }
      
      // Process ROI data
      if (roiRes.status === 'fulfilled' && roiRes.value?.data) {
        setRoi(roiRes.value.data)
        hasData = true
      } else {
        errors.push('Failed to load training ROI data')
      }
      
      // Process department comparison
      if (deptRes.status === 'fulfilled' && Array.isArray(deptRes.value?.data)) {
        setDepartments(deptRes.value.data)
        hasData = true
      } else {
        errors.push('Failed to load department comparison data')
      }
      
      // Handle errors if no data was loaded
      if (!hasData) {
        throw new Error('No data could be loaded from the server. ' + errors.join('; '))
      } else if (errors.length > 0) {
        // If we have some data but some requests failed, log the errors but don't block rendering
        console.warn('Some analytics data failed to load:', errors.join('; '))
      }
      
    } catch (error) {
      console.error('[Analytics] Error in loadAnalytics:', error)
      setError(error instanceof Error ? error.message : 'Failed to load analytics data')
    } finally {
      setLoading(false)
      setLoadingProgress('')
    }
  }

  const pieData = readiness ? [
    { name: 'High Readiness', value: readiness.distribution.high_readiness },
    { name: 'Medium Readiness', value: readiness.distribution.medium_readiness },
    { name: 'Low Readiness', value: readiness.distribution.low_readiness }
  ] : []

  console.log('[Analytics Render] Loading:', loading, 'Error:', error, 'Has Readiness:', !!readiness, 'Has ROI:', !!roi, 'Has Depts:', departments.length)

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-20">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#6B9563] mb-4"></div>
        <p className="text-[#4a4a4a] font-medium text-lg mb-2">Loading analytics data...</p>
        <p className="text-[#6B9563] text-sm animate-pulse">{loadingProgress}</p>
        <p className="text-xs text-gray-500 mt-4">This should take 2-5 seconds</p>
      </div>
    )
  }

  if (error) {
    const errorLines = error.split('\n').filter(Boolean);
    const mainError = errorLines[0] || 'An unknown error occurred';
    const details = errorLines.slice(1).filter(line => line.trim().length > 0);
    
    return (
      <div className="max-w-3xl mx-auto mt-10 px-4">
        <Card className="border-red-300 bg-red-50 shadow-lg">
          <CardHeader className="bg-red-600 text-white rounded-t-lg">
            <CardTitle className="flex items-center gap-2">
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
              <span>Unable to Load Analytics</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="p-6">
            <div className="space-y-4">
              <div className="p-4 bg-white rounded-lg border border-red-200">
                <h4 className="font-bold text-red-800 mb-2">{mainError}</h4>
                {details.length > 0 && (
                  <div className="space-y-2 mt-3">
                    {details.map((line, i) => (
                      <div key={i} className="flex items-start">
                        <span className="text-red-500 mr-2 mt-1">•</span>
                        <span className="text-red-700">{line}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
              
              <div className="bg-yellow-50 p-4 rounded-lg border border-yellow-200">
                <h4 className="font-bold text-yellow-800 mb-2 flex items-center">
                  <svg className="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  Troubleshooting Steps
                </h4>
                <ol className="list-decimal list-inside space-y-1 text-sm text-gray-700">
                  <li>Open browser developer tools (F12) and check the Console tab</li>
                  <li>Look for error messages starting with <code className="bg-gray-100 px-1.5 py-0.5 rounded">[Analytics]</code></li>
                  <li>Test the API endpoints directly:
                    <ul className="list-disc list-inside ml-6 mt-1 space-y-1">
                      <li><a href="http://localhost:5000/api/analytics/workforce-readiness" target="_blank" className="text-blue-600 hover:underline">Workforce Readiness</a></li>
                      <li><a href="http://localhost:5000/api/analytics/training-roi?time_period_days=90" target="_blank" className="text-blue-600 hover:underline">Training ROI</a></li>
                      <li><a href="http://localhost:5000/api/analytics/department-comparison" target="_blank" className="text-blue-600 hover:underline">Department Comparison</a></li>
                    </ul>
                  </li>
                  <li>Ensure the backend server is running: <code className="bg-gray-100 px-1.5 py-0.5 rounded">python app.py</code></li>
                  <li>Check if the backend is accessible at: <a href="http://localhost:5000" target="_blank" className="text-blue-600 hover:underline">http://localhost:5000</a></li>
                </ol>
              </div>
              
              <div className="flex flex-wrap gap-3 pt-2">
                <button 
                  onClick={loadAnalytics}
                  className="px-4 py-2 bg-[#6B9563] text-white rounded-lg hover:bg-[#5a7e52] transition-colors duration-200 flex items-center gap-2"
                >
                  <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                  Try Again
                </button>
                
                <button 
                  onClick={() => window.location.reload()}
                  className="px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition-colors duration-200 flex items-center gap-2"
                >
                  <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                  Refresh Page
                </button>
                
                <a 
                  href="http://localhost:5000" 
                  target="_blank" 
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors duration-200 flex items-center gap-2"
                >
                  <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                  </svg>
                  Open Backend
                </a>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  // Add debug info if no data
  if (!readiness && !roi && departments.length === 0 && !loading && !error) {
    return (
      <div className="space-y-6">
        <div className="flex items-center gap-3 animate-slide-in group">
          <BarChart3 className="h-10 w-10 text-[#6B9563]" />
          <div>
            <h1 className="text-4xl font-bold text-[#1a1a1a]">Analytics & ROI</h1>
            <p className="text-[#4a4a4a] mt-1">Track training effectiveness and return on investment</p>
          </div>
        </div>
        
        <Card>
          <CardContent className="p-8">
            <h3 className="text-lg font-bold text-gray-900 mb-4">Debug Information</h3>
            <div className="space-y-2 text-sm">
              <p>Loading: {String(loading)}</p>
              <p>Error: {error || 'None'}</p>
              <p>Has Readiness: {String(!!readiness)}</p>
              <p>Has ROI: {String(!!roi)}</p>
              <p>Departments: {departments.length}</p>
              <p className="mt-4 text-yellow-700">Data loaded but not displaying. Check console (F12) for details.</p>
              <button 
                onClick={loadAnalytics}
                className="mt-4 px-4 py-2 bg-[#6B9563] text-white rounded-lg hover:bg-[#5a7e52]"
              >
                Reload Data
              </button>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3 animate-slide-in group">
        <BarChart3 className="h-10 w-10 text-[#6B9563] transition-transform duration-300 group-hover:scale-110 group-hover:rotate-12" />
        <div>
          <h1 className="text-4xl font-bold text-[#1a1a1a] transition-all duration-300 hover:text-[#6B9563] flex items-center gap-3">
            Analytics & ROI
            <TrendingUp className="h-8 w-8 text-[#6B9563] animate-pulse opacity-70" />
          </h1>
          <p className="text-[#4a4a4a] mt-1 transition-all duration-300 hover:text-[#1a1a1a]">Track training effectiveness and return on investment</p>
        </div>
      </div>

      {/* Workforce Readiness */}
      <div ref={ref1} className="revealed">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Zap className="h-6 w-6 text-[#6B9563] animate-bounce-subtle" />
              Workforce Readiness
            </CardTitle>
          </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-3 gap-6 mb-6">
            <div className="text-center">
              <p className="text-4xl font-bold text-[#6B9563]">{readiness?.readiness_score != null ? readiness.readiness_score.toFixed(1) : '—'}</p>
              <p className="text-gray-600 mt-2">Overall Readiness Score</p>
            </div>
            <div className="text-center">
              <p className="text-4xl font-bold text-purple-600">{readiness?.total_employees}</p>
              <p className="text-gray-600 mt-2">Total Employees</p>
            </div>
            <div className="text-center">
              <p className="text-4xl font-bold text-orange-600">{readiness?.avg_skill_coverage != null ? `${readiness.avg_skill_coverage.toFixed(1)}%` : '—'}</p>
              <p className="text-gray-600 mt-2">Avg Skill Coverage</p>
            </div>
          </div>

          {pieData.length > 0 && (
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {pieData.map((_, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          )}
        </CardContent>
        </Card>
      </div>

      {/* Training ROI */}
      <div ref={ref2} className="revealed">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <DollarSign className="h-6 w-6 text-[#6B9563] animate-pulse-glow" />
              Training ROI (Last 90 Days)
            </CardTitle>
          </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-4 gap-4">
            <div>
              <p className="text-sm text-gray-600">ROI</p>
              <p className="text-2xl font-bold text-green-600">{roi?.roi_percentage != null ? `${roi.roi_percentage.toFixed(1)}%` : '—'}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Total Cost</p>
              <p className="text-2xl font-bold">{roi?.total_cost != null ? `$${roi.total_cost.toLocaleString()}` : '—'}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Estimated Benefit</p>
              <p className="text-2xl font-bold text-[#6B9563]">{roi?.estimated_benefit != null ? `$${roi.estimated_benefit.toLocaleString()}` : '—'}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Trainings</p>
              <p className="text-2xl font-bold">{roi?.total_trainings}</p>
            </div>
          </div>
        </CardContent>
        </Card>
      </div>

      {/* Department Comparison */}
      <div ref={ref3} className="revealed">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BarChart3 className="h-6 w-6 text-[#6B9563] animate-bounce-subtle" />
              Department Comparison
            </CardTitle>
          </CardHeader>
        <CardContent>
          {departments.length > 0 ? (
            <ResponsiveContainer width="100%" height={400}>
              <BarChart data={departments}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="department" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="readiness_score" fill="#3b82f6" name="Readiness Score" />
                <Bar dataKey="avg_skill_level" fill="#10b981" name="Avg Skill Level" />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <p className="text-gray-600">No department data available</p>
          )}
        </CardContent>
        </Card>
      </div>
    </div>
  )
}
