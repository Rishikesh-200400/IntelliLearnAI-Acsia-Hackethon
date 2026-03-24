import { Link, useLocation } from 'react-router-dom'
import { GraduationCap, Users, BookOpen, BarChart3, Settings, User, Library } from 'lucide-react'
import { useEffect, useRef, useState } from 'react'
import { me, getEmployee } from '@/lib/api'

const navigation = [
  { name: 'Home', href: '/', icon: GraduationCap, roles: ['guest'] },
  // Employee order: My Analytics → Courses → Course Catalog
  { name: 'My Analytics', href: '/my-analytics', icon: BarChart3, roles: ['employee'] },
  { name: 'Courses', href: '/recommendations', icon: BookOpen, roles: ['employee'] },
  { name: 'Course Catalog', href: '/course-catalog', icon: Library, roles: ['employee', 'admin'] },
  // Admin items (order: Analytics → Employees → Dashboard)
  { name: 'Analytics', href: '/analytics', icon: BarChart3, roles: ['admin'] },
  { name: 'Employees', href: '/employees', icon: Users, roles: ['admin'] },
  { name: 'Dashboard', href: '/admin', icon: Settings, roles: ['admin'] },
]

export default function Layout({ children }: { children: React.ReactNode }) {
  const location = useLocation()
  const isHomePage = location.pathname === '/'
  const role = typeof window !== 'undefined' ? (localStorage.getItem('role') || 'guest') : 'guest'
  const employeeId = typeof window !== 'undefined' ? Number(localStorage.getItem('employee_id') || 0) : 0
  const [profileOpen, setProfileOpen] = useState(false)
  const [userName, setUserName] = useState<string>('')
  const [userEmail, setUserEmail] = useState<string>('')
  const profileRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const token = typeof window !== 'undefined' ? localStorage.getItem('auth_token') : null
    if (!token || role === 'guest') return
    me()
      .then((res) => {
        if (res.data?.email) setUserEmail(res.data.email)
        if (role === 'admin') setUserName(res.data?.full_name || 'Admin')
      })
      .catch(() => {})
    if (role === 'employee' && employeeId) {
      getEmployee(employeeId)
        .then((res) => setUserName(res.data?.name || 'Employee'))
        .catch(() => {})
    }
  }, [role, employeeId])

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (!profileOpen) return
      const target = e.target as Node
      if (profileRef.current && !profileRef.current.contains(target)) {
        setProfileOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [profileOpen])

  return (
    <div className="min-h-screen bg-[#E8E5A8]">
      {/* Navigation - Hide on home page */}
      {!isHomePage && (
        <nav className="fixed top-0 left-0 right-0 z-50 bg-[#F5F2D0]/95 backdrop-blur-xl border-b border-[#D4D1A0] shadow-sm">
          <div className="w-full px-4">
            <div className="flex justify-between items-center h-16">
              {/* Logo */}
              <Link to="/" className="flex items-center space-x-2">
                <GraduationCap className="h-8 w-8 text-[#6B9563]" />
                <span className="text-2xl font-bold text-[#1a1a1a]">
                  IntelliLearn AI
                </span>
              </Link>

              {/* Navigation Links */}
              <div className="hidden md:flex items-center space-x-1">
                {navigation.filter((n)=>n.roles.includes(role as any)).map((item) => {
                  const isActive = location.pathname === item.href
                  return (
                    <Link
                      key={item.name}
                      to={item.href}
                      className={`group flex items-center space-x-2 px-4 py-2 rounded-lg text-sm font-semibold transition-all duration-300 ${
                        isActive
                          ? 'bg-[#6B9563] text-white shadow-md scale-105'
                          : 'text-[#1a1a1a] hover:bg-[#D4D1A0] hover:text-[#1a1a1a] hover:scale-105 hover:-translate-y-0.5'
                      }`}
                    >
                      <item.icon className={`h-4 w-4 transition-transform duration-300 ${isActive ? 'rotate-0' : 'group-hover:scale-110 group-hover:rotate-12'}`} />
                      <span>{item.name}</span>
                      {isActive && <span className="ml-1 w-1.5 h-1.5 rounded-full bg-white animate-pulse"></span>}
                    </Link>
                  )
                })}
                {role === 'guest' && !(location.pathname === '/login' || location.pathname === '/admin/login') && (
                  <Link
                    to="/login"
                    className="group flex items-center space-x-2 px-4 py-2 rounded-lg text-sm font-semibold transition-all duration-300 text-[#1a1a1a] hover:bg-[#D4D1A0] hover:text-[#1a1a1a] hover:scale-105 hover:-translate-y-0.5"
                  >
                    <span>Login</span>
                  </Link>
                )}
                {role !== 'guest' && (
                  <div className="relative ml-2" ref={profileRef}>
                    <button
                      onClick={() => setProfileOpen((v) => !v)}
                      className="group flex items-center space-x-2 px-4 py-2 rounded-lg text-sm font-semibold transition-all duration-300 text-[#1a1a1a] hover:bg-[#D4D1A0] hover:text-[#1a1a1a] hover:scale-105 hover:-translate-y-0.5"
                    >
                      <User className="h-4 w-4 transition-transform duration-300 group-hover:scale-110 group-hover:rotate-12" />
                      <span className="max-w-[140px] truncate">{userName || (role === 'admin' ? 'Admin' : 'Employee')}</span>
                    </button>
                    {profileOpen && (
                      <div className="absolute right-0 mt-2 w-64 bg-white border border-[#D4D1A0] rounded-lg shadow-lg z-50 p-4 space-y-2">
                        <div className="text-sm">
                          <div className={`font-semibold truncate ${role === 'admin' ? 'text-[#6B9563]' : 'text-[#1a1a1a]'}`}>{userName || (role === 'admin' ? 'Admin' : 'Employee')}</div>
                          <div className="text-[#4a4a4a] truncate">{userEmail || '—'}</div>
                        </div>
                        <div className="border-t border-[#D4D1A0] my-2"></div>
                        <button
                          onClick={() => {
                            localStorage.removeItem('auth_token')
                            localStorage.removeItem('role')
                            localStorage.removeItem('employee_id')
                            window.location.href = '/login'
                          }}
                          className="w-full text-left text-sm px-3 py-2 rounded-md hover:bg-[#F5F2D0] text-red-600"
                        >
                          Logout
                        </button>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          </div>
        </nav>
      )}

      {/* Main Content */}
      <main className={isHomePage ? '' : 'pt-16 min-h-screen'}>
        {isHomePage ? (
          <div className="animate-scale-in">{children}</div>
        ) : (
          <div className="w-full px-4 sm:px-6 lg:px-8 py-8 animate-slide-in">
            {children}
          </div>
        )}
      </main>
    </div>
  )
}
