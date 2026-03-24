import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { getEmployee, getEmployeeCourses, getEmployeeSkills } from '@/lib/api/employee'
import { getRecommendations } from '@/lib/api/recommendations'
import { useToast } from '@/components/ui/toast'

export default function EmployeeDashboard() {
  const [employee, setEmployee] = useState<any>(null)
  const [skills, setSkills] = useState<any[]>([])
  const [courses, setCourses] = useState<any[]>([])
  const [recommendations, setRecommendations] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()
  const { addToast } = useToast()
  const employeeId = localStorage.getItem('employee_id')

  useEffect(() => {
    const fetchData = async () => {
      if (!employeeId) {
        navigate('/login')
        return
      }

      try {
        setLoading(true)
        
        // Fetch employee details
        const empRes = await getEmployee(employeeId)
        setEmployee(empRes.data)
        
        // Fetch employee skills
        const skillsRes = await getEmployeeSkills(employeeId)
        setSkills(skillsRes.data || [])
        
        // Fetch employee courses
        const coursesRes = await getEmployeeCourses(employeeId)
        setCourses(coursesRes.data || [])
        
        // Fetch recommendations
        const recRes = await getRecommendations(employeeId)
        setRecommendations(recRes.data || [])
        
      } catch (error) {
        console.error('Error fetching employee data:', error)
        addToast('Failed to load employee data', 'error')
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [employeeId, navigate, addToast])

  const handleLogout = () => {
    localStorage.removeItem('auth_token')
    localStorage.removeItem('employee_id')
    navigate('/login')
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[70vh]">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900 mx-auto mb-4"></div>
          <p>Loading your dashboard...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">Welcome, {employee?.name || 'Employee'}</h1>
        <Button onClick={handleLogout} variant="outline">
          Logout
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* Employee Info Card */}
        <Card>
          <CardHeader>
            <CardTitle>My Profile</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <p><span className="font-medium">Name:</span> {employee?.name}</p>
              <p><span className="font-medium">Email:</span> {employee?.email}</p>
              <p><span className="font-medium">Department:</span> {employee?.department}</p>
              <p><span className="font-medium">Role:</span> {employee?.role}</p>
            </div>
          </CardContent>
        </Card>

        {/* Skills Card */}
        <Card>
          <CardHeader>
            <CardTitle>My Skills</CardTitle>
          </CardHeader>
          <CardContent>
            {skills.length > 0 ? (
              <div className="space-y-2">
                {skills.map((skill) => (
                  <div key={skill.id} className="flex justify-between items-center">
                    <span>{skill.name}</span>
                    <span className="text-sm text-gray-500">{skill.proficiency}%</span>
                  </div>
                ))}
              </div>
            ) : (
              <p>No skills found</p>
            )}
          </CardContent>
        </Card>

        {/* Quick Actions Card */}
        <Card>
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <Button 
              className="w-full" 
              variant="outline"
              onClick={() => navigate('/my-analytics')}
            >
              View My Analytics
            </Button>
            <Button 
              className="w-full" 
              variant="outline"
              onClick={() => navigate('/recommendations')}
            >
              View Recommendations
            </Button>
            <Button 
              className="w-full bg-[#6B9563] hover:bg-[#5a7d52]" 
              onClick={() => navigate('/learning-path')}
            >
              My Learning Path
            </Button>
            <Button 
              className="w-full" 
              variant="outline"
              onClick={() => navigate('/skill-comparison')}
            >
              Compare Skills
            </Button>
            <Button 
              className="w-full" 
              variant="outline"
              onClick={() => navigate('/course-catalog')}
            >
              Browse All Courses
            </Button>
          </CardContent>
        </Card>

        {/* My Courses */}
        {courses.length > 0 && (
          <div className="md:col-span-2 lg:col-span-3">
            <Card>
              <CardHeader>
                <CardTitle>My Enrolled Courses</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {courses.map((course) => (
                    <Card 
                      key={course.id} 
                      className="hover:shadow-md transition-shadow cursor-pointer"
                      onClick={() => navigate(`/course/${course.training_id}`)}
                    >
                      <CardHeader>
                        <CardTitle className="text-lg">{course.title}</CardTitle>
                        <p className="text-sm text-gray-500">{course.provider}</p>
                      </CardHeader>
                      <CardContent>
                        <p className="text-sm text-gray-600 mb-3 line-clamp-2">{course.description}</p>
                        <div className="space-y-2">
                          <div className="flex justify-between items-center text-sm">
                            <span className="font-medium">{course.duration} hours</span>
                            <span className={`px-2 py-1 rounded-full text-xs ${
                              course.status === 'Completed' 
                                ? 'bg-green-100 text-green-800' 
                                : 'bg-yellow-100 text-yellow-800'
                            }`}>
                              {course.status}
                            </span>
                          </div>
                          {course.assessment_score !== null && course.assessment_score !== undefined && (
                            <div className="text-sm">
                              <span className="font-medium">Score: </span>
                              <span className="text-green-600 font-bold">{course.assessment_score}%</span>
                            </div>
                          )}
                          <Button 
                            size="sm" 
                            className="w-full mt-2"
                            onClick={(e) => {
                              e.stopPropagation()
                              navigate(`/course/${course.training_id}`)
                            }}
                          >
                            View Details
                          </Button>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Recommended Courses */}
        {recommendations.length > 0 && (
          <div className="md:col-span-2 lg:col-span-3">
            <Card>
              <CardHeader>
                <CardTitle>Recommended Courses</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {recommendations.slice(0, 3).map((course: any) => (
                    <Card key={course.id} className="hover:shadow-md transition-shadow">
                      <CardHeader>
                        <CardTitle className="text-lg">{course.title}</CardTitle>
                        <p className="text-sm text-gray-500">{course.provider}</p>
                      </CardHeader>
                      <CardContent>
                        <p className="text-sm text-gray-600 mb-3 line-clamp-2">{course.description}</p>
                        <div className="flex justify-between items-center">
                          <span className="text-sm font-medium">{course.duration_hours || course.duration || 0} hours</span>
                          <Button size="sm" onClick={() => {
                            const url = course.url && String(course.url).trim().length > 0
                              ? course.url
                              : `https://www.google.com/search?q=${encodeURIComponent(`${course.title} ${course.provider || 'course'}`)}`
                            window.open(url, '_blank')
                          }}>
                            Enroll
                          </Button>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </div>
  )
}
