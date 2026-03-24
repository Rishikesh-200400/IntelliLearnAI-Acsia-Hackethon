import { useEffect, useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { getEmployeeSkillGaps, getEmployeeTrainings, getTokenSummary } from '@/lib/api'

export default function MyAnalytics() {
  const [gaps, setGaps] = useState<any[]>([])
  const [trainings, setTrainings] = useState<any[]>([])
  const [tokens, setTokens] = useState<number>(0)
  const employeeId = typeof window !== 'undefined' ? Number(localStorage.getItem('employee_id') || 0) : 0

  // Derived admin-like KPIs for this employee
  const completedCount = trainings.filter((t:any) => t.status === 'Completed').length
  const inProgressCount = trainings.filter((t:any) => t.status !== 'Completed').length
  const avgScore = (() => {
    const scores = trainings.map((t:any) => t.assessment_score).filter((s:any) => s !== null && s !== undefined)
    if (scores.length === 0) return 0
    const sum = scores.reduce((a:number, b:number) => a + Number(b || 0), 0)
    return Math.round((sum / scores.length) * 10) / 10
  })()


  const loadAll = async () => {
    if (!employeeId) return
    try { const r1 = await getEmployeeSkillGaps(employeeId); setGaps(r1.data || []) } catch {}
    try { const r2 = await getEmployeeTrainings(employeeId); setTrainings(r2.data || []) } catch {}
    try {
      const r3 = await getTokenSummary()
      const ts = Array.isArray(r3.data) ? r3.data.find((t:any)=> t.employee_id === employeeId) : null
      setTokens(ts ? (ts.tokens || 0) : 0)
    } catch {}
  }

  useEffect(() => { loadAll() }, [employeeId])

  if (!employeeId) {
    return <div className="text-center py-16">Please sign in as an employee to view your analytics.</div>
  }

  return (
    <div className="space-y-6">
      {/* Overview KPIs similar to Admin, but scoped to this employee */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>My Overview</CardTitle>
            <Button variant="outline" onClick={loadAll}>
              Refresh
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
            <div>
              <p className="text-sm text-gray-600">Tokens</p>
              <p className="text-3xl font-bold text-[#6B9563]">{tokens}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Completed</p>
              <p className="text-3xl font-bold text-green-600">{completedCount}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">In Progress</p>
              <p className="text-3xl font-bold text-yellow-600">{inProgressCount}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Avg Score</p>
              <p className="text-3xl font-bold text-blue-600">{avgScore}%</p>
            </div>
          </div>
        </CardContent>
      </Card>
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>My Rewards</CardTitle>
            <Button variant="outline" onClick={loadAll}>
              Refresh
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-6">
            <div>
              <p className="text-sm text-gray-600">Tokens Earned</p>
              <p className="text-3xl font-bold text-[#6B9563]">{tokens}</p>
            </div>
          </div>
        </CardContent>
      </Card>
      <Card>
        <CardHeader>
          <CardTitle>My Skill Gaps</CardTitle>
        </CardHeader>
        <CardContent>
          {gaps.length === 0 ? (
            <p className="text-gray-600">No active gaps found.</p>
          ) : (
            <ul className="list-disc pl-5">
              {gaps.map((g, i) => (
                <li key={i}>{g.skill_name} — Gap {g.gap_score} ({g.priority})</li>
              ))}
            </ul>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>My Trainings</CardTitle>
        </CardHeader>
        <CardContent>
          {trainings.length === 0 ? (
            <p className="text-gray-600">No trainings recorded.</p>
          ) : (
            <div className="overflow-auto">
              <table className="min-w-full text-sm">
                <thead>
                  <tr className="text-left text-gray-600 border-b">
                    <th className="py-2 pr-4">Course</th>
                    <th className="py-2 pr-4">Status</th>
                    <th className="py-2 pr-4">Progress</th>
                    <th className="py-2 pr-4">Link</th>
                  </tr>
                </thead>
                <tbody>
                  {trainings.map((t:any, i:number)=> (
                    <tr key={i} className="border-b last:border-0">
                      <td className="py-2 pr-4">{t.course_title}</td>
                      <td className="py-2 pr-4">{t.status}</td>
                      <td className="py-2 pr-4">{t.progress_percentage}%</td>
                      <td className="py-2 pr-4">{t.course_url ? <a className="text-blue-600 underline" href={t.course_url} target="_blank" rel="noreferrer">View</a> : '—'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}


