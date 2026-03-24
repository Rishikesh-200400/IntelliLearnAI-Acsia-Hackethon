import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { useToast } from '@/components/ui/toast'
import api from '@/lib/api'

interface Question {
  id: number
  question: string
  options: string[]
  correct_answer: number
}

export default function Assessment() {
  const { trainingId } = useParams()
  const navigate = useNavigate()
  const { addToast } = useToast()
  const [training, setTraining] = useState<any>(null)
  const [course, setCourse] = useState<any>(null)
  const [questions, setQuestions] = useState<Question[]>([])
  const [answers, setAnswers] = useState<{ [key: number]: number }>({})
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [showResults, setShowResults] = useState(false)
  const [score, setScore] = useState(0)

  useEffect(() => {
    fetchAssessment()
  }, [trainingId])

  const fetchAssessment = async () => {
    try {
      setLoading(true)
      
      // Fetch training details
      const trainingRes = await api.get(`/api/trainings/${trainingId}`)
      setTraining(trainingRes.data)

      // Fetch course details
      const courseRes = await api.get(`/api/courses/${trainingRes.data.course_id}`)
      setCourse(courseRes.data)

      // Generate assessment questions
      const assessmentRes = await api.post(`/api/trainings/${trainingId}/generate-assessment`)
      setQuestions(assessmentRes.data.questions || [])

    } catch (error) {
      console.error('Error fetching assessment:', error)
      addToast('Failed to load assessment', 'error')
      navigate(`/course/${trainingId}`)
    } finally {
      setLoading(false)
    }
  }

  const handleAnswerChange = (questionId: number, answerIndex: number) => {
    setAnswers({ ...answers, [questionId]: answerIndex })
  }

  const handleSubmit = async () => {
    // Check if all questions are answered
    if (Object.keys(answers).length < questions.length) {
      addToast('Please answer all questions', 'error')
      return
    }

    try {
      setSubmitting(true)
      
      // Submit answers
      const response = await api.post(`/api/trainings/${trainingId}/submit-assessment`, {
        answers: Object.values(answers)
      })

      setScore(response.data.score)
      setShowResults(true)
      addToast(`Assessment completed! Score: ${response.data.score}%`, 'success')

    } catch (error) {
      console.error('Error submitting assessment:', error)
      addToast('Failed to submit assessment', 'error')
    } finally {
      setSubmitting(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[70vh]">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900 mx-auto mb-4"></div>
          <p>Loading assessment...</p>
        </div>
      </div>
    )
  }

  if (showResults) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-2xl mx-auto">
          <Card>
            <CardHeader>
              <CardTitle className="text-3xl text-center">Assessment Results</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="text-center">
                <div className={`text-6xl font-bold mb-4 ${
                  score >= 80 ? 'text-green-600' : score >= 60 ? 'text-yellow-600' : 'text-red-600'
                }`}>
                  {score}%
                </div>
                <p className="text-xl text-gray-700 mb-2">
                  {score >= 80 ? '🎉 Excellent!' : score >= 60 ? '👍 Good Job!' : '📚 Keep Learning!'}
                </p>
                <p className="text-gray-600">
                  You answered {Math.round((score / 100) * questions.length)} out of {questions.length} questions correctly
                </p>
              </div>

              <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                <p className="text-sm text-blue-800 text-center">
                  Your score has been recorded and your profile has been updated.
                </p>
              </div>

              <div className="flex gap-4">
                <Button 
                  className="flex-1" 
                  onClick={() => navigate(`/course/${trainingId}`)}
                >
                  View Course Details
                </Button>
                <Button 
                  className="flex-1" 
                  variant="outline"
                  onClick={() => navigate('/employee/dashboard')}
                >
                  Back to Dashboard
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    )
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <Button 
        variant="outline" 
        onClick={() => navigate(`/course/${trainingId}`)}
        className="mb-6"
      >
        ← Cancel Assessment
      </Button>

      <div className="max-w-3xl mx-auto space-y-6">
        {/* Assessment Header */}
        <Card>
          <CardHeader>
            <CardTitle className="text-2xl">Assessment: {course?.title}</CardTitle>
            <p className="text-gray-600 mt-2">
              Answer all questions to complete the assessment. Passing score: 60%
            </p>
          </CardHeader>
          <CardContent>
            <div className="flex justify-between items-center p-4 bg-gray-50 rounded-lg">
              <span className="font-medium">Total Questions: {questions.length}</span>
              <span className="font-medium">Time: Unlimited</span>
            </div>
          </CardContent>
        </Card>

        {/* Questions */}
        {questions.map((question, index) => (
          <Card key={question.id}>
            <CardHeader>
              <CardTitle className="text-lg">
                Question {index + 1} of {questions.length}
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-gray-800 font-medium">{question.question}</p>
              
              <div className="space-y-2">
                {question.options.map((option, optionIndex) => (
                  <label
                    key={optionIndex}
                    className={`flex items-center p-4 border rounded-lg cursor-pointer transition-all ${
                      answers[question.id] === optionIndex
                        ? 'border-blue-500 bg-blue-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <input
                      type="radio"
                      name={`question-${question.id}`}
                      value={optionIndex}
                      checked={answers[question.id] === optionIndex}
                      onChange={() => handleAnswerChange(question.id, optionIndex)}
                      className="mr-3"
                    />
                    <span>{option}</span>
                  </label>
                ))}
              </div>
            </CardContent>
          </Card>
        ))}

        {/* Submit Button */}
        <Card>
          <CardContent className="pt-6">
            <div className="space-y-4">
              <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                <p className="text-sm text-yellow-800 text-center">
                  ⚠️ Make sure you've answered all questions before submitting
                </p>
              </div>
              
              <Button 
                className="w-full" 
                size="lg"
                onClick={handleSubmit}
                disabled={submitting || Object.keys(answers).length < questions.length}
              >
                {submitting ? 'Submitting...' : '📝 Submit Assessment'}
              </Button>

              <p className="text-sm text-gray-500 text-center">
                Questions answered: {Object.keys(answers).length} / {questions.length}
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

