import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { getEmployee, getEmployeeSkills, getEmployeeSkillGaps, getEmployeeTrainings, predictSkillGaps, getTokenSummary } from '@/lib/api'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

export default function EmployeeDetail() {
  const { id } = useParams()
  const [employee, setEmployee] = useState<any>(null)
  const [skills, setSkills] = useState<any[]>([])
  const [skillGaps, setSkillGaps] = useState<any[]>([])
  const [trainings, setTrainings] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [reload, setReload] = useState(0)
  const [tokens, setTokens] = useState<number>(0)

  useEffect(() => {
    const loadEmployeeData = async () => {
      setLoading(true)
      try {
        const [empRes, skillsRes, gapsRes, trainingsRes] = await Promise.all([
          getEmployee(Number(id)),
          getEmployeeSkills(Number(id)),
          getEmployeeSkillGaps(Number(id)),
          getEmployeeTrainings(Number(id))
        ])
        
        setEmployee(empRes.data)
        setSkills(skillsRes.data)
        setSkillGaps(gapsRes.data)
        setTrainings(trainingsRes.data)
        // Fetch tokens separately and ignore failures
        try {
          const tokenRes = await getTokenSummary()
          const ts = Array.isArray(tokenRes.data) ? tokenRes.data.find((t:any)=> t.employee_id === Number(id)) : null
          setTokens(ts ? (ts.tokens || 0) : 0)
        } catch {}
      } catch (error) {
        console.error('Failed to load employee data:', error)
      } finally {
        setLoading(false)
      }
    }
    
    loadEmployeeData()
  }, [id, reload])

  const handlePredictSkillGaps = async () => {
    try {
      await predictSkillGaps(Number(id))
      setReload(prev => prev + 1)
    } catch (error) {
      console.error('Failed to predict skill gaps:', error)
    }
  }

  if (loading) {
    return <div className="text-center py-20">Loading...</div>
  }

  if (!employee) {
    return <div className="text-center py-20">Employee not found</div>
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="text-3xl">{employee.name}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-4 gap-4">
            <div>
              <p className="text-sm text-gray-600">Role</p>
              <p className="text-lg font-semibold">{employee.role || 'N/A'}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Experience</p>
              <p className="text-lg font-semibold">{employee.years_of_experience || 0} years</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Email</p>
              <p className="text-lg font-semibold">{employee.email}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Tokens</p>
              <p className="text-lg font-semibold text-[#6B9563]">{tokens}</p>
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="grid md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Skills Overview</CardTitle>
          </CardHeader>
          <CardContent>
            {skills.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={skills}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="skill_name" angle={-45} textAnchor="end" height={100} />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="proficiency_level" fill="#3b82f6" />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <p className="text-gray-600">No skills recorded</p>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Skill Gaps</CardTitle>
            <Button size="sm" onClick={handlePredictSkillGaps}>Predict Gaps</Button>
          </CardHeader>
          <CardContent>
            {skillGaps.length > 0 ? (
              <div className="space-y-3">
                {skillGaps.slice(0, 5).map((gap, idx) => (
                  <div key={idx} className="p-3 bg-gray-50 rounded-lg">
                    <div className="flex justify-between items-start">
                      <div>
                        <p className="font-semibold">{gap.skill_name}</p>
                        <p className="text-sm text-gray-600">
                          Current: {gap.current_level} | Required: {gap.required_level}
                        </p>
                      </div>
                      <span className={`px-2 py-1 text-xs rounded ${
                        gap.priority === 'High' ? 'bg-red-100 text-red-800' :
                        gap.priority === 'Medium' ? 'bg-orange-100 text-orange-800' :
                        'bg-green-100 text-green-800'
                      }`}>
                        {gap.priority}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-600">No skill gaps identified. Click "Predict Gaps" to analyze.</p>
            )}
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Training History</CardTitle>
        </CardHeader>
        <CardContent>
          {trainings.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-2 text-left">Course</th>
                    <th className="px-4 py-2 text-left">Provider</th>
                    <th className="px-4 py-2 text-left">Link</th>
                    <th className="px-4 py-2 text-left">Status</th>
                    <th className="px-4 py-2 text-left">Progress</th>
                    <th className="px-4 py-2 text-left">Score</th>
                  </tr>
                </thead>
                <tbody>
                  {trainings.map((training, idx) => (
                    <tr key={idx} className="border-t">
                      <td className="px-4 py-2">{training.course_title}</td>
                      <td className="px-4 py-2">{training.course_provider}</td>
                      <td className="px-4 py-2">{training.course_url ? <a className="text-blue-600 underline" href={training.course_url} target="_blank" rel="noreferrer">View</a> : '—'}</td>
                      <td className="px-4 py-2">{training.status}</td>
                      <td className="px-4 py-2">{training.progress_percentage}%</td>
                      <td className="px-4 py-2">{training.assessment_score || 'N/A'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p className="text-gray-600">No training records found</p>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
