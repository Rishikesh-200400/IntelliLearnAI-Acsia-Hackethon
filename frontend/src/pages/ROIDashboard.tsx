import { useEffect, useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import api from '@/lib/api'
import { DollarSign, TrendingUp, Award, Clock } from 'lucide-react'

export default function ROIDashboard() {
  const [metrics, setMetrics] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  const loadData = async () => {
    try {
      setLoading(true)
      const res = await api.get('/api/analytics/roi-metrics')
      setMetrics(res.data)
    } catch (error) {
      console.error('Error loading ROI metrics:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadData()
  }, [])

  if (loading) {
    return <div className="flex justify-center items-center min-h-screen">Loading...</div>
  }

  if (!metrics) {
    return <div className="text-center py-16">No ROI data available</div>
  }

  const isPositiveROI = metrics.roi_percentage > 0

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <DollarSign className="h-10 w-10 text-green-600" />
          <div>
            <h1 className="text-4xl font-bold text-gray-900">ROI Dashboard</h1>
            <p className="text-gray-600 mt-1">Training investment return and business impact metrics</p>
          </div>
        </div>
        <Button onClick={loadData} variant="outline">Refresh</Button>
      </div>

      {/* ROI Overview */}
      <Card className={`border-2 ${isPositiveROI ? 'border-green-500' : 'border-orange-500'}`}>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-6 w-6" />
            Overall ROI
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center">
            <p className={`text-6xl font-bold ${isPositiveROI ? 'text-green-600' : 'text-orange-600'}`}>
              {metrics.roi_percentage > 0 ? '+' : ''}{metrics.roi_percentage}%
            </p>
            <p className="text-gray-600 mt-2">
              {isPositiveROI ? 'Positive Return on Investment' : 'Investment in Progress'}
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-sm text-gray-600 flex items-center gap-2">
              <DollarSign className="h-4 w-4" />
              Total Investment
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold text-blue-600">${metrics.total_investment.toLocaleString()}</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm text-gray-600 flex items-center gap-2">
              <TrendingUp className="h-4 w-4" />
              Estimated Value
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold text-green-600">${metrics.estimated_value.toLocaleString()}</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm text-gray-600 flex items-center gap-2">
              <Award className="h-4 w-4" />
              Completion Rate
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold text-purple-600">{metrics.completion_rate}%</p>
            <p className="text-sm text-gray-600 mt-1">
              {metrics.completed_trainings} of {metrics.total_trainings}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm text-gray-600 flex items-center gap-2">
              <Clock className="h-4 w-4" />
              Training Hours
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold text-orange-600">{metrics.training_hours.toLocaleString()}</p>
          </CardContent>
        </Card>
      </div>

      {/* Cost Breakdown */}
      <Card>
        <CardHeader>
          <CardTitle>Investment Breakdown</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex justify-between items-center p-4 bg-blue-50 rounded-lg">
              <div>
                <p className="font-medium">Direct Course Costs</p>
                <p className="text-sm text-gray-600">Course fees and materials</p>
              </div>
              <p className="text-2xl font-bold text-blue-600">
                ${metrics.cost_breakdown.direct_course_costs.toLocaleString()}
              </p>
            </div>

            <div className="flex justify-between items-center p-4 bg-orange-50 rounded-lg">
              <div>
                <p className="font-medium">Time Investment</p>
                <p className="text-sm text-gray-600">Employee time at $50/hour</p>
              </div>
              <p className="text-2xl font-bold text-orange-600">
                ${metrics.cost_breakdown.time_investment.toLocaleString()}
              </p>
            </div>

            <div className="flex justify-between items-center p-4 bg-green-50 rounded-lg">
              <div>
                <p className="font-medium">Value Generated</p>
                <p className="text-sm text-gray-600">Tokens at $10 each ({metrics.total_tokens_awarded} tokens)</p>
              </div>
              <p className="text-2xl font-bold text-green-600">
                ${metrics.estimated_value.toLocaleString()}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Performance Metrics */}
      <Card>
        <CardHeader>
          <CardTitle>Training Performance</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center p-6 bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg">
              <p className="text-sm text-gray-600 mb-2">Completed Trainings</p>
              <p className="text-4xl font-bold text-blue-600">{metrics.completed_trainings}</p>
            </div>

            <div className="text-center p-6 bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg">
              <p className="text-sm text-gray-600 mb-2">Average Assessment Score</p>
              <p className="text-4xl font-bold text-purple-600">{metrics.average_score}%</p>
            </div>

            <div className="text-center p-6 bg-gradient-to-br from-green-50 to-green-100 rounded-lg">
              <p className="text-sm text-gray-600 mb-2">Tokens Awarded</p>
              <p className="text-4xl font-bold text-green-600">{metrics.total_tokens_awarded}</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Insights */}
      <Card>
        <CardHeader>
          <CardTitle>Key Insights</CardTitle>
        </CardHeader>
        <CardContent>
          <ul className="space-y-3">
            <li className="flex items-start gap-3">
              <div className={`w-2 h-2 ${isPositiveROI ? 'bg-green-600' : 'bg-orange-600'} rounded-full mt-2`}></div>
              <div>
                <p className="font-medium">ROI Trend</p>
                <p className="text-sm text-gray-600">
                  {isPositiveROI 
                    ? `Training investments are generating positive returns. Continue current strategy.`
                    : `ROI is building. As employees complete more courses and apply skills, returns will increase.`}
                </p>
              </div>
            </li>
            <li className="flex items-start gap-3">
              <div className="w-2 h-2 bg-purple-600 rounded-full mt-2"></div>
              <div>
                <p className="font-medium">Completion Performance</p>
                <p className="text-sm text-gray-600">
                  {metrics.completion_rate >= 70 
                    ? `Strong completion rate of ${metrics.completion_rate}% indicates good engagement.`
                    : `Consider incentives to improve completion rate (currently ${metrics.completion_rate}%).`}
                </p>
              </div>
            </li>
            <li className="flex items-start gap-3">
              <div className="w-2 h-2 bg-blue-600 rounded-full mt-2"></div>
              <div>
                <p className="font-medium">Assessment Quality</p>
                <p className="text-sm text-gray-600">
                  Average score of {metrics.average_score}% shows strong knowledge retention.
                </p>
              </div>
            </li>
          </ul>
        </CardContent>
      </Card>
    </div>
  )
}

