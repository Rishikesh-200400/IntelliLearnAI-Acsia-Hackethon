import { useEffect, useState } from 'react'
import { Settings, Upload, Cpu, Users } from 'lucide-react'
import { getEmployees } from '@/lib/api'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { getDataSummary, importSampleData, trainModels, getTokenSummary } from '@/lib/api'

export default function Admin() {
  const [summary, setSummary] = useState<any>(null)
  const [importing, setImporting] = useState(false)
  const [training, setTraining] = useState(false)
  const [message, setMessage] = useState('')
  const [employees, setEmployees] = useState<any[]>([])
  const [tokenSummary, setTokenSummary] = useState<any[]>([])

  useEffect(() => {
    loadSummary()
    loadEmployees()
    loadTokens()
  }, [])
  const loadEmployees = async () => {
    try {
      const res = await getEmployees()
      setEmployees(res.data)
    } catch (e) {
      // ignore
    }
  }

  const loadTokens = async () => {
    try {
      const res = await getTokenSummary()
      setTokenSummary(res.data)
    } catch (e) {
      // ignore
    }
  }

  

  const loadSummary = async () => {
    try {
      const response = await getDataSummary()
      setSummary(response.data)
    } catch (error) {
      console.error('Failed to load summary:', error)
    }
  }

  const handleImport = async () => {
    setImporting(true)
    setMessage('')
    try {
      const response = await importSampleData()
      setMessage(response.data.message)
      loadSummary()
    } catch (error) {
      setMessage('Import failed: ' + (error as any).message)
    } finally {
      setImporting(false)
    }
  }

  const handleTrain = async () => {
    setTraining(true)
    setMessage('')
    try {
      const response = await trainModels()
      if (response.data.status === 'success') {
        setMessage('Models trained successfully!')
      } else {
        setMessage(response.data.status)
      }
    } catch (error) {
      setMessage('Training failed: ' + (error as any).message)
    } finally {
      setTraining(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <Settings className="h-10 w-10 text-blue-600" />
        <div>
          <h1 className="text-4xl font-bold text-gray-900">Admin Dashboard</h1>
          <p className="text-gray-600 mt-1">Manage data, load samples, and train models</p>
        </div>
      </div>

      

      {/* Data Summary */}
      <Card>
        <CardHeader>
          <CardTitle>System Overview</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-5 gap-4 text-center">
            <div>
              <p className="text-3xl font-bold text-blue-600">{summary?.total_employees || 0}</p>
              <p className="text-gray-600 mt-2">Employees</p>
            </div>
            <div>
              <p className="text-3xl font-bold text-purple-600">{summary?.total_skills || 0}</p>
              <p className="text-gray-600 mt-2">Skills</p>
            </div>
            <div>
              <p className="text-3xl font-bold text-orange-600">{summary?.total_courses || 0}</p>
              <p className="text-gray-600 mt-2">Courses</p>
            </div>
            <div>
              <p className="text-3xl font-bold text-green-600">{summary?.total_trainings || 0}</p>
              <p className="text-gray-600 mt-2">Trainings</p>
            </div>
            <div>
              <p className="text-3xl font-bold text-cyan-600">{summary?.avg_skills_per_employee.toFixed(1) || 0}</p>
              <p className="text-gray-600 mt-2">Avg Skills/Emp</p>
            </div>
            <div>
              <p className="text-3xl font-bold text-[#6B9563]">{tokenSummary.reduce((a: number, t: any) => a + (t.tokens || 0), 0)}</p>
              <p className="text-gray-600 mt-2">Total Tokens</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Employees quick view */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2"><Users className="h-5 w-5"/>Employees</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-auto">
            <table className="min-w-full text-sm">
              <thead>
                <tr className="text-left text-gray-600 border-b">
                  <th className="py-2 pr-4">Name</th>
                  <th className="py-2 pr-4">Email</th>
                  <th className="py-2 pr-4">Role</th>
                  <th className="py-2 pr-4">Experience</th>
                  <th className="py-2 pr-4">Tokens</th>
                </tr>
              </thead>
              <tbody>
                {employees.slice(0, 10).map((e: any) => {
                  const ts = tokenSummary.find((t:any) => t.employee_id === e.id)
                  return (
                  <tr key={e.id} className="border-b last:border-0">
                    <td className="py-2 pr-4">{e.name}</td>
                    <td className="py-2 pr-4">{e.email}</td>
                    <td className="py-2 pr-4">{e.role || '-'}</td>
                    <td className="py-2 pr-4">{e.years_of_experience || 0} yrs</td>
                    <td className="py-2 pr-4 font-semibold text-[#6B9563]">{ts ? ts.tokens : 0}</td>
                  </tr>
                )})}
                {employees.length === 0 && (
                  <tr><td className="py-2 text-gray-500">No employees found.</td></tr>
                )}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* Actions */}
      <div className="grid md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Upload className="h-5 w-5" />
              Data Import
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-gray-600 mb-4">
              Load sample data including employees, skills, courses, and training history.
            </p>
            <Button 
              className="w-full" 
              onClick={handleImport} 
              disabled={importing}
            >
              {importing ? 'Importing...' : 'Import Sample Data'}
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Cpu className="h-5 w-5" />
              Model Training
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-gray-600 mb-4">
              Train machine learning models for skill gap prediction using available data.
            </p>
            <Button 
              className="w-full" 
              onClick={handleTrain} 
              disabled={training}
            >
              {training ? 'Training...' : 'Train ML Models'}
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* Message */}
      {message && (
        <Card className={message.includes('failed') || message.includes('Error') ? 'border-red-300' : 'border-green-300'}>
          <CardContent className="py-4">
            <p className={message.includes('failed') || message.includes('Error') ? 'text-red-600' : 'text-green-600'}>
              {message}
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
