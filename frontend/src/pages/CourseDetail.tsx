import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { useToast } from '@/components/ui/toast'
import api from '@/lib/api'

export default function CourseDetail() {
  const { trainingId } = useParams()
  const navigate = useNavigate()
  const { addToast } = useToast()
  const [training, setTraining] = useState<any>(null)
  const [course, setCourse] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [completing, setCompleting] = useState(false)

  useEffect(() => {
    fetchTrainingDetails()
  }, [trainingId])

  const fetchTrainingDetails = async () => {
    try {
      setLoading(true)
      const response = await api.get(`/api/trainings/${trainingId}`)
      setTraining(response.data)
      
      // Fetch course details
      const courseRes = await api.get(`/api/courses/${response.data.course_id}`)
      setCourse(courseRes.data)
    } catch (error) {
      console.error('Error fetching training details:', error)
      addToast('Failed to load course details', 'error')
    } finally {
      setLoading(false)
    }
  }

  const handleCompleteCourse = async () => {
    try {
      setCompleting(true)
      await api.post(`/api/trainings/${trainingId}/complete`)
      addToast('Course marked as completed!', 'success')
      fetchTrainingDetails() // Refresh data
    } catch (error) {
      console.error('Error completing course:', error)
      addToast('Failed to complete course', 'error')
    } finally {
      setCompleting(false)
    }
  }

  const handleStartAssessment = () => {
    navigate(`/assessment/${trainingId}`)
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[70vh]">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900 mx-auto mb-4"></div>
          <p>Loading course details...</p>
        </div>
      </div>
    )
  }

  const isCompleted = training?.status === 'Completed'
  const hasAssessment = training?.has_assessment

  return (
    <div className="container mx-auto px-4 py-8">
      <Button 
        variant="outline" 
        onClick={() => navigate(-1)}
        className="mb-6"
      >
        ← Back to Dashboard
      </Button>

      <div className="max-w-4xl mx-auto space-y-6">
        {/* Course Header */}
        <Card>
          <CardHeader>
            <CardTitle className="text-3xl">{course?.title}</CardTitle>
            <div className="flex items-center gap-4 text-sm text-gray-600 mt-2">
              <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full">
                {course?.category}
              </span>
              <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full">
                {course?.difficulty_level}
              </span>
              <span>⏱️ {course?.duration_hours} hours</span>
              <span>⭐ {course?.rating}/5</span>
            </div>
          </CardHeader>
          <CardContent>
            <p className="text-gray-700 text-lg mb-4">{course?.description}</p>
            <p className="text-sm text-gray-600">
              <span className="font-medium">Provider:</span> {course?.provider}
            </p>
          </CardContent>
        </Card>

        {/* Course Status */}
        <Card>
          <CardHeader>
            <CardTitle>Course Status</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="font-medium">Status:</span>
                <span className={`px-3 py-1 rounded-full text-sm ${
                  isCompleted ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                }`}>
                  {training?.status}
                </span>
              </div>
              
              <div className="flex justify-between items-center">
                <span className="font-medium">Progress:</span>
                <span>{training?.progress_percentage || 0}%</span>
              </div>

              <div className="flex justify-between items-center">
                <span className="font-medium">Enrollment Date:</span>
                <span>{new Date(training?.enrollment_date).toLocaleDateString()}</span>
              </div>

              {training?.completion_date && (
                <div className="flex justify-between items-center">
                  <span className="font-medium">Completion Date:</span>
                  <span>{new Date(training?.completion_date).toLocaleDateString()}</span>
                </div>
              )}

              {training?.assessment_score !== null && training?.assessment_score !== undefined && (
                <div className="flex justify-between items-center">
                  <span className="font-medium">Assessment Score:</span>
                  <span className="text-lg font-bold text-green-600">
                    {training?.assessment_score}%
                  </span>
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Course Link */}
        {course?.url && (
          <Card>
            <CardHeader>
              <CardTitle>Course Materials</CardTitle>
            </CardHeader>
            <CardContent>
              <Button 
                className="w-full" 
                onClick={() => window.open(course.url, '_blank')}
              >
                🔗 Open Course Website
              </Button>
            </CardContent>
          </Card>
        )}

        {/* Action Buttons */}
        <Card>
          <CardHeader>
            <CardTitle>Actions</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {!isCompleted && (
              <div>
                <Button 
                  className="w-full" 
                  onClick={handleCompleteCourse}
                  disabled={completing}
                  size="lg"
                >
                  {completing ? 'Completing...' : '✅ Mark Course as Completed'}
                </Button>
                <p className="text-sm text-gray-500 mt-2 text-center">
                  Click this button after you've finished all course materials
                </p>
              </div>
            )}

            {isCompleted && (
              <div className="space-y-3">
                <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                  <p className="text-green-800 font-medium">
                    ✅ Course Completed Successfully!
                  </p>
                  <p className="text-sm text-green-700 mt-1">
                    You can now take the assessment to test your knowledge.
                  </p>
                </div>

                <Button 
                  className="w-full" 
                  onClick={handleStartAssessment}
                  size="lg"
                  variant={training?.assessment_score !== null ? "outline" : "default"}
                >
                  {training?.assessment_score !== null 
                    ? '📝 Retake Assessment' 
                    : '🎯 Start Assessment'}
                </Button>

                {training?.assessment_score !== null && (
                  <div className="text-center p-4 bg-blue-50 border border-blue-200 rounded-lg">
                    <p className="text-sm text-blue-800">
                      Previous Assessment Score: <span className="font-bold">{training?.assessment_score}%</span>
                    </p>
                  </div>
                )}
              </div>
            )}

            {!isCompleted && (
              <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                <p className="text-yellow-800 text-sm">
                  ⚠️ Assessment will be unlocked after you complete the course
                </p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

