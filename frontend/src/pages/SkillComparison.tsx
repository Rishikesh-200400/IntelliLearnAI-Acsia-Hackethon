import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import api from '@/lib/api'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { Target, TrendingUp } from 'lucide-react'

export default function SkillComparison() {
  const [employee, setEmployee] = useState<any>(null)
  const [skillGaps, setSkillGaps] = useState<any[]>([])
  const [recommendations, setRecommendations] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()
  const employeeId = localStorage.getItem('employee_id')

  useEffect(() => {
    const loadData = async () => {
      if (!employeeId) {
        navigate('/login')
        return
      }

      try {
        setLoading(true)
        // Get employee info
        const empRes = await api.get(`/api/employees/${employeeId}`)
        setEmployee(empRes.data)

        // Get skill gaps
        const gapsRes = await api.get(`/api/employees/${employeeId}/skill-gaps`)
        setSkillGaps(gapsRes.data)

        // Get recommendations
        const recsRes = await api.get(`/api/recommendations/${employeeId}?top_n=10`)
        setRecommendations(recsRes.data.recommendations || [])
      } catch (error) {
        console.error('Error loading data:', error)
      } finally {
        setLoading(false)
      }
    }

    loadData()
  }, [employeeId, navigate])

  if (loading) {
    return <div className="flex justify-center items-center min-h-screen">Loading...</div>
  }

  if (!employee || skillGaps.length === 0) {
    return (
      <div className="text-center py-16">
        <p className="text-xl text-gray-600 mb-4">No skill gaps identified yet.</p>
        <Button onClick={() => navigate('/employee/dashboard')}>Back to Dashboard</Button>
      </div>
    )
  }

  // Prepare data for comparison chart
  const comparisonData = skillGaps.map((gap) => ({
    skill: gap.skill_name,
    'Current Level': gap.current_level,
    'Required Level': gap.required_level,
    priority: gap.priority
  }))

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Target className="h-10 w-10 text-[#6B9563]" />
          <div>
            <h1 className="text-4xl font-bold text-gray-900">Skill Gap Analysis</h1>
            <p className="text-gray-600 mt-1">
              Current vs Required Skills for {employee.name}
            </p>
          </div>
        </div>
        <Button onClick={() => navigate('/employee/dashboard')} variant="outline">
          Back to Dashboard
        </Button>
      </div>

      {/* Skill Comparison Chart */}
      <Card>
        <CardHeader>
          <CardTitle>Current vs Required Skill Levels</CardTitle>
        </CardHeader>
        <CardContent style={{ height: 400 }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={comparisonData} margin={{ top: 20, right: 30, left: 20, bottom: 70 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="skill" angle={-20} textAnchor="end" height={80} interval={0} />
              <YAxis domain={[0, 10]} label={{ value: 'Skill Level (0-10)', angle: -90, position: 'insideLeft' }} />
              <Tooltip />
              <Legend />
              <Bar dataKey="Current Level" fill="#6B9563" radius={[4, 4, 0, 0]} />
              <Bar dataKey="Required Level" fill="#ef4444" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Detailed Skill Gaps Table */}
      <Card>
        <CardHeader>
          <CardTitle>Skill Gap Details</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="min-w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Skill
                  </th>
                  <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Current Level
                  </th>
                  <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Required Level
                  </th>
                  <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Gap
                  </th>
                  <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Priority
                  </th>
                  <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Progress
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {skillGaps.map((gap, index) => {
                  const progressPercent = (gap.current_level / gap.required_level) * 100
                  return (
                    <tr key={index}>
                      <td className="px-6 py-4 whitespace-nowrap font-medium text-gray-900">
                        {gap.skill_name}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-center">
                        <span className="text-lg font-semibold text-green-600">{gap.current_level}</span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-center">
                        <span className="text-lg font-semibold text-red-600">{gap.required_level}</span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-center">
                        <span className="text-lg font-bold text-orange-600">{gap.gap_score}</span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-center">
                        <span
                          className={`px-3 py-1 rounded-full text-xs font-semibold ${
                            gap.priority === 'High'
                              ? 'bg-red-100 text-red-800'
                              : gap.priority === 'Medium'
                              ? 'bg-yellow-100 text-yellow-800'
                              : 'bg-blue-100 text-blue-800'
                          }`}
                        >
                          {gap.priority}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center gap-2">
                          <div className="flex-1 bg-gray-200 rounded-full h-2">
                            <div
                              className="bg-green-600 h-2 rounded-full"
                              style={{ width: `${progressPercent}%` }}
                            ></div>
                          </div>
                          <span className="text-xs font-medium">{Math.round(progressPercent)}%</span>
                        </div>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* Recommended Courses Based on Gaps */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5" />
            Recommended Courses to Bridge Gaps
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-gray-600 mb-4">
            These courses are recommended based on your skill gaps. Courses addressing <strong>High Priority</strong> gaps are shown first.
          </p>
          {recommendations.length === 0 ? (
            <p className="text-gray-600">No recommendations available.</p>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {recommendations.slice(0, 6).map((course: any) => (
                <Card
                  key={course.id}
                  className={`hover:shadow-lg transition-shadow ${
                    course.priority === 'High'
                      ? 'border-2 border-red-500'
                      : course.priority === 'Medium'
                      ? 'border-2 border-yellow-500'
                      : ''
                  }`}
                >
                  <CardHeader>
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <CardTitle className="text-lg">{course.title}</CardTitle>
                        <p className="text-sm text-gray-500">{course.provider}</p>
                      </div>
                      {course.priority && (
                        <span
                          className={`px-2 py-1 rounded-full text-xs font-semibold ml-2 ${
                            course.priority === 'High'
                              ? 'bg-red-100 text-red-800'
                              : course.priority === 'Medium'
                              ? 'bg-yellow-100 text-yellow-800'
                              : 'bg-blue-100 text-blue-800'
                          }`}
                        >
                          {course.priority}
                        </span>
                      )}
                    </div>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm text-gray-600 line-clamp-2 mb-3">{course.description}</p>
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span>Duration:</span>
                        <span className="font-medium">{course.duration_hours || 0}h</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span>Match:</span>
                        <span className="font-medium text-green-600">
                          {Math.round((course.match_score || 0) * 100)}%
                        </span>
                      </div>
                      <Button
                        size="sm"
                        className="w-full mt-2"
                        onClick={() => {
                          const url =
                            course.url && course.url.trim()
                              ? course.url
                              : `https://www.google.com/search?q=${encodeURIComponent(
                                  `${course.title} ${course.provider || 'course'}`
                                )}`
                          window.open(url, '_blank')
                        }}
                      >
                        View Course
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* How It Works */}
      <Card className="bg-blue-50">
        <CardHeader>
          <CardTitle>How Course Recommendations Work</CardTitle>
        </CardHeader>
        <CardContent>
          <ol className="list-decimal list-inside space-y-2 text-sm text-gray-700">
            <li>
              <strong>Skill Gap Identification:</strong> The system compares your current skill levels with the
              required levels for your role.
            </li>
            <li>
              <strong>Gap Score Calculation:</strong> Gap Score = Required Level - Current Level. Higher gaps get
              higher priority.
            </li>
            <li>
              <strong>Priority Assignment:</strong> High priority for gaps ≥ 4, Medium for gaps 2-3, Low for gaps &lt; 2.
            </li>
            <li>
              <strong>Course Matching:</strong> Courses are matched to your skill gaps using AI and keyword analysis.
            </li>
            <li>
              <strong>Priority Sorting:</strong> Courses addressing <span className="text-red-600 font-semibold">High Priority</span> gaps appear first, followed by <span className="text-yellow-600 font-semibold">Medium</span> and <span className="text-blue-600 font-semibold">Low</span>.
            </li>
            <li>
              <strong>Match Score:</strong> Indicates how well the course addresses your specific skill gaps (0-100%).
            </li>
          </ol>
        </CardContent>
      </Card>
    </div>
  )
}

