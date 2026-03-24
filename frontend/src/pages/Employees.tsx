import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Users, Sparkles } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { getEmployees, getTokenSummary } from '@/lib/api'
import { useScrollReveal } from '@/hooks/useScrollReveal'

interface Employee {
  id: number
  name: string
  email: string
  role: string
  department: string
  years_of_experience: number
}

export default function Employees() {
  const navigate = useNavigate()
  const [employees, setEmployees] = useState<Employee[]>([])
  const [loading, setLoading] = useState(true)
  const [tokenSummary, setTokenSummary] = useState<any[]>([])

  useEffect(() => {
    loadEmployees()
    loadTokens()
  }, [])

  const loadEmployees = async () => {
    try {
      const response = await getEmployees()
      setEmployees(response.data)
    } catch (error) {
      console.error('Failed to load employees:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadTokens = async () => {
    try {
      const res = await getTokenSummary()
      setTokenSummary(res.data || [])
    } catch {}
  }

  if (loading) {
    return <div className="text-center py-20">Loading...</div>
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between animate-slide-in">
        <div>
          <h1 className="text-4xl font-bold text-[#1a1a1a] flex items-center gap-3 group">
            <Users className="h-10 w-10 text-[#6B9563] transition-transform duration-300 group-hover:scale-110 group-hover:rotate-12" />
            <span className="transition-all duration-300 hover:text-[#6B9563]">Employees</span>
            <Sparkles className="h-6 w-6 text-[#6B9563] animate-pulse opacity-70" />
          </h1>
          <p className="text-[#4a4a4a] mt-2 transition-all duration-300 hover:text-[#1a1a1a]">Manage and view employee information</p>
        </div>
      </div>

      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
        {employees.map((employee, index) => {
          const ts = tokenSummary.find((t:any)=> t.employee_id === employee.id)
          return (
            <EmployeeCard key={employee.id} employee={employee} navigate={navigate} index={index} tokens={ts ? ts.tokens : 0} />
          )
        })}
      </div>
    </div>
  )
}

function EmployeeCard({ employee, navigate, index, tokens }: { employee: any, navigate: any, index: number, tokens: number }) {
  const ref = useScrollReveal()
  
  return (
    <div ref={ref} className="revealed group" style={{ animationDelay: `${index * 0.1}s` }}>
      <Card className="hover:shadow-2xl cursor-pointer">
        <CardHeader>
          <CardTitle className="text-xl flex items-center justify-between group-hover:text-[#6B9563] transition-colors duration-300">
            {employee.name}
            <Users className="h-5 w-5 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2 text-sm">
            <p><span className="font-semibold">Email:</span> {employee.email}</p>
            <p><span className="font-semibold">Role:</span> {employee.role || 'N/A'}</p>
            <p><span className="font-semibold">Experience:</span> {employee.years_of_experience || 0} years</p>
            <p><span className="font-semibold">Tokens:</span> <span className="text-[#6B9563] font-semibold">{tokens}</span></p>
            <Button 
              variant="outline" 
              size="sm" 
              className="w-full mt-4"
              onClick={() => navigate(`/employees/${employee.id}`)}
            >
              View Details
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
