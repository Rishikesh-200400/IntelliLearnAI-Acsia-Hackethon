import { useState, useEffect } from 'react'
import { BookOpen } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { getEmployees, getRecommendations } from '@/lib/api'

export default function Recommendations() {
  const [employees, setEmployees] = useState<any[]>([])
  const [selectedEmployee, setSelectedEmployee] = useState<number | null>(null)
  const [recommendations, setRecommendations] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  const role = typeof window !== 'undefined' ? localStorage.getItem('role') : null
  const storedEmployeeId = typeof window !== 'undefined' ? Number(localStorage.getItem('employee_id') || 0) : 0

  useEffect(() => {
    if (role === 'employee' && storedEmployeeId) {
      setSelectedEmployee(storedEmployeeId)
      // Auto-load for the logged-in employee
      loadRecommendations(storedEmployeeId)
    } else {
      loadEmployees()
    }
  }, [])

  const loadEmployees = async () => {
    try {
      const response = await getEmployees()
      setEmployees(response.data)
      if (response.data.length > 0) {
        setSelectedEmployee(response.data[0].id)
      }
    } catch (error) {
      console.error('Failed to load employees:', error)
    }
  }

  const loadRecommendations = async (employeeIdOverride?: number) => {
    const empId = employeeIdOverride || selectedEmployee
    if (!empId) return
    setLoading(true)

    try {
      const response = await getRecommendations(empId, 10)
      setRecommendations(response.data.recommendations || [])
    } catch (error) {
      console.error('Failed to load recommendations:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <BookOpen className="h-10 w-10 text-[#6B9563]" />
        <div>
          <h1 className="text-4xl font-bold text-[#1a1a1a]">Course Recommendations</h1>
          <p className="text-[#4a4a4a] mt-1">AI-powered personalized course suggestions</p>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Generate Recommendations</CardTitle>
        </CardHeader>
        <CardContent>
          {role === 'employee' ? (
            <div className="flex gap-4">
              <Button onClick={() => loadRecommendations(storedEmployeeId)} disabled={loading}>
                {loading ? 'Loading...' : 'Show My Recommendations'}
              </Button>
            </div>
          ) : (
            <div className="flex gap-4">
              <select 
                className="flex-1 px-4 py-3 border-2 border-[#D4D1A0] rounded-lg bg-white text-[#1a1a1a] font-medium focus:outline-none cursor-pointer hover:border-[#6B9563] hover:shadow-md transition-all duration-200"
                value={selectedEmployee || ''}
                onChange={(e) => setSelectedEmployee(Number(e.target.value))}
              >
                <option value="">Select an employee...</option>
                {employees.map(emp => (
                  <option key={emp.id} value={emp.id}>{emp.name}</option>
                ))}
              </select>
              <Button onClick={() => loadRecommendations()} disabled={loading || !selectedEmployee}>
                {loading ? 'Loading...' : 'Generate Recommendations'}
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      {recommendations.length > 0 && (
        <div className="grid md:grid-cols-2 gap-6">
          {recommendations.map((rec, idx) => (
            <Card key={idx}>
              <CardHeader>
                <CardTitle className="text-xl">{rec.title || rec.course_title}</CardTitle>
                <p className="text-sm text-gray-600">{rec.provider}</p>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-sm font-semibold">Match Score:</span>
                    <span className="text-[#6B9563] font-bold">{rec.recommendation_score?.toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm">Category:</span>
                    <span className="text-sm">{rec.category}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm">Difficulty:</span>
                    <span className="text-sm">{rec.difficulty_level}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm">Duration:</span>
                    <span className="text-sm">{rec.duration_hours} hours</span>
                  </div>
                  {rec.reasoning && (
                    <div className="mt-3 p-3 bg-[#D4D1A0]/50 rounded-lg">
                      <p className="text-sm">{rec.reasoning}</p>
                    </div>
                  )}
                  {rec.url && (
                    <a href={rec.url} target="_blank" rel="noopener noreferrer" className="block mt-3">
                      <Button variant="outline" size="sm" className="w-full">
                        View Course
                      </Button>
                    </a>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
