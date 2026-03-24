import { useEffect, useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import api from '@/lib/api'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'
import { AlertTriangle, TrendingUp, Users } from 'lucide-react'

export default function SkillGapAnalysis() {
  const [overview, setOverview] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  const loadData = async () => {
    try {
      setLoading(true)
      const res = await api.get('/api/analytics/skill-gap-overview')
      setOverview(res.data)
    } catch (error) {
      console.error('Error loading skill gap overview:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleAutoRecommend = async () => {
    try {
      await api.post('/api/skill-gaps/auto-recommend', {})
      alert('Course recommendations generated for all employees with skill gaps!')
    } catch (error) {
      console.error('Error generating recommendations:', error)
      alert('Failed to generate recommendations')
    }
  }

  useEffect(() => {
    loadData()
  }, [])

  if (loading) {
    return <div className="flex justify-center items-center min-h-screen">Loading...</div>
  }

  if (!overview) {
    return <div className="text-center py-16">No skill gap data available</div>
  }

  const COLORS = ['#ef4444', '#f59e0b', '#3b82f6']

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <AlertTriangle className="h-10 w-10 text-orange-600" />
          <div>
            <h1 className="text-4xl font-bold text-gray-900">Skill Gap Analysis</h1>
            <p className="text-gray-600 mt-1">Organization-wide skill gap overview and insights</p>
          </div>
        </div>
        <div className="flex gap-3">
          <Button onClick={loadData} variant="outline">Refresh</Button>
          <Button onClick={handleAutoRecommend}>Auto-Generate Recommendations</Button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-sm text-gray-600">Total Skill Gaps</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-4xl font-bold text-orange-600">{overview.total_gaps}</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm text-gray-600">High Priority</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-4xl font-bold text-red-600">{overview.high_priority}</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm text-gray-600">Employees Affected</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-4xl font-bold text-blue-600">{overview.employees_with_gaps}</p>
            <p className="text-sm text-gray-600 mt-1">of {overview.total_employees} total</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm text-gray-600">Coverage</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-4xl font-bold text-green-600">{overview.coverage_percentage}%</p>
          </CardContent>
        </Card>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Priority Distribution</CardTitle>
          </CardHeader>
          <CardContent style={{ height: 300 }}>
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={overview.priority_distribution}
                  dataKey="count"
                  nameKey="priority"
                  cx="50%"
                  cy="50%"
                  outerRadius={100}
                  label
                >
                  {overview.priority_distribution.map((entry: any, index: number) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Top Skill Gaps Across Organization</CardTitle>
          </CardHeader>
          <CardContent style={{ height: 300 }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={overview.top_skill_gaps} margin={{ left: -20, bottom: 40 }}>
                <XAxis dataKey="skill" angle={-20} textAnchor="end" height={80} interval={0} />
                <YAxis />
                <Tooltip />
                <Bar dataKey="count" fill="#f59e0b" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Action Cards */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5" />
            Recommended Actions
          </CardTitle>
        </CardHeader>
        <CardContent>
          <ul className="space-y-3">
            <li className="flex items-start gap-3">
              <div className="w-2 h-2 bg-red-600 rounded-full mt-2"></div>
              <div>
                <p className="font-medium">Address High-Priority Gaps</p>
                <p className="text-sm text-gray-600">
                  {overview.high_priority} high-priority skill gaps require immediate attention
                </p>
              </div>
            </li>
            <li className="flex items-start gap-3">
              <div className="w-2 h-2 bg-blue-600 rounded-full mt-2"></div>
              <div>
                <p className="font-medium">Generate Course Recommendations</p>
                <p className="text-sm text-gray-600">
                  Use auto-recommend to assign relevant courses to employees with skill gaps
                </p>
              </div>
            </li>
            <li className="flex items-start gap-3">
              <div className="w-2 h-2 bg-green-600 rounded-full mt-2"></div>
              <div>
                <p className="font-medium">Monitor Progress</p>
                <p className="text-sm text-gray-600">
                  Track course completion rates and reassess skill levels quarterly
                </p>
              </div>
            </li>
          </ul>
        </CardContent>
      </Card>
    </div>
  )
}

