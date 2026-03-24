import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import api from '@/lib/api'
import { Target, BookOpen, TrendingUp, AlertCircle } from 'lucide-react'

export default function LearningPath() {
  const [pathData, setPathData] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()
  const employeeId = localStorage.getItem('employee_id')

  const loadPath = async () => {
    if (!employeeId) return

    try {
      setLoading(true)
      const res = await api.get(`/api/employees/${employeeId}/learning-path`)
      setPathData(res.data)
    } catch (error) {
      console.error('Error loading learning path:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadPath()
  }, [employeeId])

  if (loading) {
    return <div className="flex justify-center items-center min-h-screen">Loading your personalized learning path...</div>
  }

  if (!pathData) {
    return <div className="text-center py-16">Unable to load learning path. Please try again.</div>
  }

  const { employee, skill_gaps, recommended_courses, current_trainings } = pathData

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <Target className="h-10 w-10 text-[#6B9563]" />
        <div>
          <h1 className="text-4xl font-bold text-gray-900">My Learning Path</h1>
          <p className="text-gray-600 mt-1">
            Personalized course recommendations for {employee.name}
          </p>
        </div>
      </div>

      {/* Employee Info */}
      <Card>
        <CardHeader>
          <CardTitle>Profile Overview</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <p className="text-sm text-gray-600">Role</p>
              <p className="font-medium">{employee.role || 'N/A'}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Department</p>
              <p className="font-medium">{employee.department || 'N/A'}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Active Gaps</p>
              <p className="font-medium text-orange-600">{skill_gaps.length}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">In Progress</p>
              <p className="font-medium text-blue-600">{current_trainings.length}</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Skill Gaps */}
      {skill_gaps.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <AlertCircle className="h-5 w-5 text-orange-600" />
              Identified Skill Gaps
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {skill_gaps.slice(0, 5).map((gap: any, index: number) => (
                <div
                  key={index}
                  className={`p-4 rounded-lg border-l-4 ${
                    gap.priority === 'High'
                      ? 'border-red-500 bg-red-50'
                      : gap.priority === 'Medium'
                      ? 'border-yellow-500 bg-yellow-50'
                      : 'border-blue-500 bg-blue-50'
                  }`}
                >
                  <div className="flex justify-between items-start">
                    <div>
                      <p className="font-medium">{gap.skill_name}</p>
                      <p className="text-sm text-gray-600 mt-1">
                        Current: {gap.current_level || 0} | Required: {gap.required_level || 0} | Gap: {gap.gap_score}
                      </p>
                    </div>
                    <span
                      className={`px-3 py-1 rounded-full text-xs font-medium ${
                        gap.priority === 'High'
                          ? 'bg-red-100 text-red-800'
                          : gap.priority === 'Medium'
                          ? 'bg-yellow-100 text-yellow-800'
                          : 'bg-blue-100 text-blue-800'
                      }`}
                    >
                      {gap.priority}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Current Trainings */}
      {current_trainings.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BookOpen className="h-5 w-5 text-blue-600" />
              Courses In Progress
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {current_trainings.map((training: any, index: number) => (
                <div key={index} className="p-4 border rounded-lg">
                  <p className="font-medium">{training.course_title}</p>
                  <p className="text-sm text-gray-600 mt-1">Status: {training.status}</p>
                  <div className="mt-2">
                    <div className="flex justify-between text-sm mb-1">
                      <span>Progress</span>
                      <span className="font-medium">{training.progress}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-blue-600 h-2 rounded-full"
                        style={{ width: `${training.progress}%` }}
                      ></div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Recommended Courses */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5 text-green-600" />
            Recommended Courses to Bridge Gaps
          </CardTitle>
        </CardHeader>
        <CardContent>
          {recommended_courses.length === 0 ? (
            <p className="text-gray-600">No recommendations available yet.</p>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {recommended_courses.slice(0, 9).map((course: any) => (
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
                    <p className="text-sm text-gray-600 line-clamp-2 mb-3">
                      {course.description}
                    </p>
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span>Duration:</span>
                        <span className="font-medium">{course.duration_hours || 0}h</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span>Level:</span>
                        <span className="font-medium">{course.difficulty_level || 'N/A'}</span>
                      </div>
                      {course.match_score && (
                        <div className="flex justify-between text-sm">
                          <span>Match:</span>
                          <span className="font-medium text-green-600">{Math.round(course.match_score * 100)}%</span>
                        </div>
                      )}
                      <Button
                        size="sm"
                        className="w-full mt-2"
                        onClick={() => {
                          const url = course.url && course.url.trim()
                            ? course.url
                            : `https://www.google.com/search?q=${encodeURIComponent(`${course.title} ${course.provider || 'course'}`)}`
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
    </div>
  )
}

