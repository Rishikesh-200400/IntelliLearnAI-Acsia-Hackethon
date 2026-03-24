import { useState, useEffect, useRef } from 'react'
import { Bot, Send, Loader2, Sparkles } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { getEmployees, sendChatMessage, getPersonalizedGuidance } from '@/lib/api'

export default function AIAssistant() {
  const [employees, setEmployees] = useState<any[]>([])
  const [selectedEmployee, setSelectedEmployee] = useState<number | null>(null)
  const [messages, setMessages] = useState<any[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [sources, setSources] = useState<string[]>([])
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const role = typeof window !== 'undefined' ? localStorage.getItem('role') : null

  useEffect(() => {
    // For employee dashboard, lock to the logged-in employee
    const eid = Number(localStorage.getItem('employee_id') || 0)
    if (eid) setSelectedEmployee(eid)
  }, [])

  // Load persisted chat per employee
  useEffect(() => {
    if (!selectedEmployee) return
    const key = `chat_history_${selectedEmployee}`
    try {
      const raw = localStorage.getItem(key)
      if (raw) {
        const parsed = JSON.parse(raw)
        setMessages(Array.isArray(parsed) ? parsed : [])
      } else {
        setMessages([])
      }
    } catch {
      setMessages([])
    }
    setSources([])
  }, [selectedEmployee])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const loadEmployees = async () => {
    try {
      const res = await getEmployees()
      const list = res.data || []
      setEmployees(list)
      // If admin and no employee selected yet, default to first employee
      if (role === 'admin' && !selectedEmployee && list.length > 0) {
        setSelectedEmployee(list[0].id)
      }
    } catch {}
  }

  // If admin, load employees for selector
  useEffect(() => {
    if (role === 'admin') {
      loadEmployees()
    }
  }, [role])

  const persistMessages = (empId: number, msgs: any[]) => {
    try {
      localStorage.setItem(`chat_history_${empId}`, JSON.stringify(msgs))
    } catch {}
  }

  const handleSend = async () => {
    if (!input.trim() || !selectedEmployee) return

    const userMessage = { role: 'user', content: input }
    setMessages(prev => {
      const next = [...prev, userMessage]
      persistMessages(selectedEmployee, next)
      return next
    })
    setInput('')
    setLoading(true)

    try {
      const response = await sendChatMessage(selectedEmployee, input)
      const assistantMessage = { 
        role: 'assistant', 
        content: response.data.answer || response.data.fallback_answer || 'Sorry, I encountered an issue.'
      }
      setMessages(prev => {
        const next = [...prev, assistantMessage]
        persistMessages(selectedEmployee, next)
        return next
      })
      if (response.data?.source_documents?.length) {
        setSources(response.data.source_documents as string[])
      } else {
        setSources([])
      }
    } catch (error) {
      console.error('Chat error:', error)
      setMessages(prev => {
        const next = [...prev, { role: 'assistant', content: 'Error: Unable to get response' }]
        persistMessages(selectedEmployee, next)
        return next
      })
    } finally {
      setLoading(false)
    }
  }

  const handleGetGuidance = async () => {
    if (!selectedEmployee) return
    setLoading(true)

    try {
      const response = await getPersonalizedGuidance(selectedEmployee)
      const guidance = response.data
      const message = {
        role: 'assistant',
        content: `📋 Personalized Guidance:\n\n${guidance.recommendations || 'No guidance available'}`
      }
      setMessages(prev => {
        const next = [...prev, message]
        persistMessages(selectedEmployee, next)
        return next
      })
    } catch (error) {
      console.error('Guidance error:', error)
    } finally {
      setLoading(false)
    }
  }

  const quickPrompts = [
    'What are my top skill gaps and how do I fix them?',
    'Recommend 3 courses to become a better backend engineer.',
    'Create a 4-week learning plan for cloud and Kubernetes.',
  ]

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <Bot className="h-10 w-10 text-[#6B9563]" />
        <div>
          <h1 className="text-4xl font-bold text-[#1a1a1a]">AI Learning Assistant</h1>
          <p className="text-[#4a4a4a] mt-1">Get personalized learning guidance and career advice</p>
        </div>
      </div>

      <div className="grid md:grid-cols-3 gap-6">
        <div className="md:col-span-1">
          <Card>
            <CardHeader>
              <CardTitle>Your Assistant</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-gray-700">This assistant is personalized to your profile.</p>
              <Button className="w-full mt-4" onClick={handleGetGuidance} disabled={!selectedEmployee}>
                Get Personalized Guidance
              </Button>

              {role === 'admin' && (
                <div className="mt-6">
                  <label className="block text-sm mb-1">Chat as employee</label>
                  <select
                    className="w-full border rounded-md p-2"
                    value={selectedEmployee || ''}
                    onChange={(e) => setSelectedEmployee(Number(e.target.value) || null)}
                  >
                    <option value="">Select employee</option>
                    {employees.map((e) => (
                      <option key={e.id} value={e.id}>{e.name} ({e.email})</option>
                    ))}
                  </select>
                </div>
              )}

              <div className="mt-6">
                <p className="text-sm font-semibold mb-2 text-[#1a1a1a] flex items-center gap-2"><Sparkles className="h-4 w-4 text-[#6B9563]"/> Try these prompts</p>
                <div className="flex flex-col gap-2">
                  {quickPrompts.map((q) => (
                    <button
                      key={q}
                      onClick={() => setInput(q)}
                      className="text-left text-sm px-3 py-2 rounded-md border border-[#D4D1A0] hover:border-[#6B9563] transition-colors"
                    >
                      {q}
                    </button>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="md:col-span-2">
          <Card className="h-[700px] flex flex-col overflow-hidden">
            <CardHeader>
              <CardTitle>Chat</CardTitle>
            </CardHeader>
            <CardContent className="flex-1 flex flex-col overflow-hidden">
              <div className="flex-1 overflow-y-auto overflow-x-hidden space-y-4 mb-4 pr-2">
                {messages.map((msg, idx) => (
                  <div key={idx} className={`flex w-full min-w-0 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                    <div className={`max-w-full md:max-w-[80%] p-3 rounded-lg min-w-0 ${
                      msg.role === 'user' 
                        ? 'bg-[#6B9563] text-white' 
                        : 'bg-[#D4D1A0]/50 text-[#1a1a1a]'
                    }`} style={{ wordBreak: 'break-word', overflowWrap: 'anywhere' }}>
                      <p className="whitespace-pre-wrap break-words" style={{ wordBreak: 'break-word', overflowWrap: 'anywhere' }}>{msg.content}</p>
                    </div>
                  </div>
                ))}
                {loading && (
                  <div className="flex justify-start">
                    <div className="max-w-[80%] p-3 rounded-lg bg-[#D4D1A0]/50 text-[#1a1a1a] flex items-center gap-2">
                      <Loader2 className="h-4 w-4 animate-spin" />
                      <span>IntelliLearn AI is typing…</span>
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>

              <div className="flex gap-2">
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && !loading && handleSend()}
                  placeholder="Ask me anything..."
                  className="flex-1 px-4 py-3 border-2 border-[#D4D1A0] rounded-lg bg-white text-[#1a1a1a] font-medium focus:outline-none placeholder:text-gray-400 hover:border-[#6B9563] disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
                  disabled={loading || !selectedEmployee}
                />
                <Button onClick={handleSend} disabled={loading || !input.trim() || !selectedEmployee}>
                  <Send className="h-5 w-5" />
                </Button>
              </div>

              {sources.length > 0 && (
                <div className="mt-4 border-t pt-3">
                  <p className="text-sm font-semibold mb-2">Sources</p>
                  <ul className="list-disc pl-5 space-y-1 text-sm text-gray-700">
                    {sources.slice(0, 5).map((s, i) => (
                      <li key={i} className="break-words">{s}</li>
                    ))}
                  </ul>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
