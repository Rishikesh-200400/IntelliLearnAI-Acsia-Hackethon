import { useEffect, useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { BookOpen, ExternalLink, Search, Filter } from 'lucide-react'
import api from '@/lib/api'
import { useToast } from '@/components/ui/toast'

export default function CourseCatalog() {
  const [courses, setCourses] = useState<any[]>([])
  const [filteredCourses, setFilteredCourses] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedProvider, setSelectedProvider] = useState<string>('all')
  const { addToast } = useToast()

  useEffect(() => {
    fetchCourses()
  }, [])

  useEffect(() => {
    filterCourses()
  }, [searchTerm, selectedProvider, courses])

  const fetchCourses = async () => {
    try {
      setLoading(true)
      // Get all courses from the database
      const response = await api.get('/api/courses')
      setCourses(response.data || [])
      setFilteredCourses(response.data || [])
    } catch (error) {
      console.error('Error fetching courses:', error)
      addToast('Failed to load courses', 'error')
    } finally {
      setLoading(false)
    }
  }

  const filterCourses = () => {
    let filtered = [...courses]

    // Filter by search term
    if (searchTerm) {
      filtered = filtered.filter(
        (course) =>
          course.title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
          course.description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
          course.provider?.toLowerCase().includes(searchTerm.toLowerCase())
      )
    }

    // Filter by provider
    if (selectedProvider !== 'all') {
      filtered = filtered.filter(
        (course) => course.provider === selectedProvider
      )
    }

    setFilteredCourses(filtered)
  }

  const providers = Array.from(new Set(courses.map((c) => c.provider).filter(Boolean)))

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[70vh]">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900 mx-auto mb-4"></div>
          <p>Loading course catalog...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="flex items-center gap-3 mb-6">
        <BookOpen className="h-10 w-10 text-blue-600" />
        <div>
          <h1 className="text-4xl font-bold text-gray-900">Course Catalog</h1>
          <p className="text-gray-600 mt-1">Browse all available courses</p>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <Card>
          <CardContent className="pt-6">
            <p className="text-3xl font-bold text-blue-600">{courses.length}</p>
            <p className="text-gray-600 mt-1">Total Courses</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <p className="text-3xl font-bold text-purple-600">{providers.length}</p>
            <p className="text-gray-600 mt-1">Providers</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <p className="text-3xl font-bold text-orange-600">
              {Math.round(courses.reduce((acc, c) => acc + (c.duration_hours || 0), 0) / courses.length || 0)}h
            </p>
            <p className="text-gray-600 mt-1">Avg Duration</p>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <Card className="mb-6">
        <CardContent className="pt-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Search */}
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search courses..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            {/* Provider Filter */}
            <div className="relative">
              <Filter className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
              <select
                value={selectedProvider}
                onChange={(e) => setSelectedProvider(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 appearance-none bg-white"
              >
                <option value="all">All Providers</option>
                {providers.map((provider) => (
                  <option key={provider} value={provider}>
                    {provider}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Results count */}
          <p className="text-sm text-gray-600 mt-3">
            Showing {filteredCourses.length} of {courses.length} courses
          </p>
        </CardContent>
      </Card>

      {/* Course Grid */}
      {filteredCourses.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center">
            <BookOpen className="h-16 w-16 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500">No courses found matching your criteria</p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredCourses.map((course) => (
            <Card key={course.id} className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <CardTitle className="text-lg">{course.title}</CardTitle>
                <p className="text-sm text-gray-500">{course.provider || 'Unknown Provider'}</p>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-gray-600 mb-4 line-clamp-3">
                  {course.description || 'No description available'}
                </p>
                
                <div className="space-y-2 mb-4">
                  <div className="flex justify-between items-center text-sm">
                    <span className="text-gray-600">Duration:</span>
                    <span className="font-medium">{course.duration_hours || 0} hours</span>
                  </div>
                  <div className="flex justify-between items-center text-sm">
                    <span className="text-gray-600">Format:</span>
                    <span className="font-medium">{course.format || 'Online'}</span>
                  </div>
                  {course.level && (
                    <div className="flex justify-between items-center text-sm">
                      <span className="text-gray-600">Level:</span>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        course.level === 'Beginner' ? 'bg-green-100 text-green-800' :
                        course.level === 'Intermediate' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-red-100 text-red-800'
                      }`}>
                        {course.level}
                      </span>
                    </div>
                  )}
                </div>

                <Button
                  className="w-full"
                  onClick={() => {
                    const url = course.url && String(course.url).trim().length > 0
                      ? course.url
                      : `https://www.google.com/search?q=${encodeURIComponent(`${course.title} ${course.provider || 'course'}`)}`
                    window.open(url, '_blank')
                  }}
                >
                  <ExternalLink className="h-4 w-4 mr-2" />
                  View Course
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}

