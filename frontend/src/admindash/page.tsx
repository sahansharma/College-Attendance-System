
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { BookOpen, Users, Calendar, TrendingUp, TrendingDown, ArrowRight, Clock } from "lucide-react"
import { AttendanceChart } from "@/components/attendance-chart"
import { RecentAttendance } from "@/components/recent-attendance"
import { getClassCount, getStudentCount, getRecentAttendance, getAttendanceTrend } from "@/lib/api"
import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { Badge } from "@/components/ui/badge"

export default function DashboardPage() {
  const [classCount, setClassCount] = useState(0)
  const [studentCount, setStudentCount] = useState(0)
  const [recentAttendance, setRecentAttendance] = useState([])
  const [attendanceTrend, setAttendanceTrend] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    async function fetchDashboardData() {
      try {
        const [classes, students, attendance, trend] = await Promise.all([
          getClassCount(),
          getStudentCount(),
          getRecentAttendance(),
          getAttendanceTrend(),
        ])
        setClassCount(classes)
        setStudentCount(students)
        setRecentAttendance(attendance)
        setAttendanceTrend(trend)
        setLoading(false)
      } catch (err) {
        console.error("Error fetching dashboard data:", err)
        setError(err.message)
        setLoading(false)
      }
    }

    fetchDashboardData()
  }, [])

  if (error)
    return (
      <div className="rounded-lg border bg-card text-card-foreground shadow-sm p-6 text-red-500">
        <div className="flex items-center gap-2">
          <div className="rounded-full bg-red-100 p-2 dark:bg-red-900/20">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              className="h-5 w-5 text-red-600"
            >
              <circle cx="12" cy="12" r="10" />
              <line x1="12" x2="12" y1="8" y2="12" />
              <line x1="12" x2="12.01" y1="16" y2="16" />
            </svg>
          </div>
          <div>
            <h3 className="font-medium">Error loading dashboard data</h3>
            <p className="text-sm text-muted-foreground">{error}</p>
          </div>
        </div>
      </div>
    )

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
          <p className="text-muted-foreground">Overview of attendance statistics and recent activity</p>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant="outline" className="text-xs">
            <Clock className="mr-1 h-3 w-3" />
            Last updated: {new Date().toLocaleTimeString()}
          </Badge>
          <Button size="sm">Refresh Data</Button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {/* Total Classes Card */}
        <Card className="overflow-hidden">
          <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
            <CardTitle className="text-sm font-medium">Total Classes</CardTitle>
            <div className="p-2 bg-primary/10 rounded-full">
              <BookOpen className="h-4 w-4 text-primary" />
            </div>
          </CardHeader>
          <CardContent>
            {loading ? <Skeleton className="h-8 w-20" /> : <div className="text-3xl font-bold">{classCount}</div>}
            <p className="text-xs text-muted-foreground mt-1">Across all departments</p>
          </CardContent>
          <div className="bg-muted/50 px-6 py-2">
            <div className="text-xs text-muted-foreground flex items-center">
              <TrendingUp className="h-3 w-3 mr-1 text-green-500" />
              <span className="text-green-500 font-medium">+2.5%</span>
              <span className="ml-1">from last semester</span>
            </div>
          </div>
        </Card>

        {/* Total Students Card */}
        <Card className="overflow-hidden">
          <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
            <CardTitle className="text-sm font-medium">Total Students</CardTitle>
            <div className="p-2 bg-blue-500/10 rounded-full">
              <Users className="h-4 w-4 text-blue-500" />
            </div>
          </CardHeader>
          <CardContent>
            {loading ? <Skeleton className="h-8 w-20" /> : <div className="text-3xl font-bold">{studentCount}</div>}
            <p className="text-xs text-muted-foreground mt-1">Currently enrolled</p>
          </CardContent>
          <div className="bg-muted/50 px-6 py-2">
            <div className="text-xs text-muted-foreground flex items-center">
              <TrendingUp className="h-3 w-3 mr-1 text-green-500" />
              <span className="text-green-500 font-medium">+5.2%</span>
              <span className="ml-1">from previous year</span>
            </div>
          </div>
        </Card>

        {/* Today's Attendance Card */}
        <Card className="overflow-hidden">
          <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
            <CardTitle className="text-sm font-medium">Today's Attendance</CardTitle>
            <div className="p-2 bg-green-500/10 rounded-full">
              <Calendar className="h-4 w-4 text-green-500" />
            </div>
          </CardHeader>
          <CardContent>
            {loading ? <Skeleton className="h-8 w-20" /> : <div className="text-3xl font-bold">87%</div>}
            <p className="text-xs text-muted-foreground mt-1">Average across all classes</p>
          </CardContent>
          <div className="bg-muted/50 px-6 py-2">
            <div className="text-xs text-muted-foreground flex items-center">
              <TrendingDown className="h-3 w-3 mr-1 text-amber-500" />
              <span className="text-amber-500 font-medium">-1.3%</span>
              <span className="ml-1">from yesterday</span>
            </div>
          </div>
        </Card>
      </div>

      {/* Charts and Tables */}
      <div className="grid gap-6 md:grid-cols-2">
        {/* Attendance Trend Chart */}
        <Card className="col-span-1">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <div>
              <CardTitle>Attendance Trend</CardTitle>
              <CardDescription>Weekly attendance percentage</CardDescription>
            </div>
          </CardHeader>
          <CardContent className="pt-4">
            {loading ? (
              <div className="space-y-2">
                <Skeleton className="h-[240px] w-full" />
              </div>
            ) : (
              <AttendanceChart data={attendanceTrend} />
            )}
          </CardContent>
        </Card>

        {/* Recent Attendance */}
        <Card className="col-span-1">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <div>
              <CardTitle>Recent Attendance</CardTitle>
              <CardDescription>Latest attendance records</CardDescription>
            </div>
            <Button variant="outline" size="sm" className="h-8 gap-1">
              <span className="hidden sm:inline">View All</span>
              <ArrowRight className="h-3.5 w-3.5" />
            </Button>
          </CardHeader>
          <CardContent className="pt-4">
            {loading ? (
              <div className="space-y-2">
                <Skeleton className="h-12 w-full" />
                <Skeleton className="h-12 w-full" />
                <Skeleton className="h-12 w-full" />
                <Skeleton className="h-12 w-full" />
              </div>
            ) : (
              <RecentAttendance data={recentAttendance} />
            )}
          </CardContent>
          <CardFooter className="border-t bg-muted/50 px-6 py-3">
            <div className="flex justify-between items-center w-full text-xs text-muted-foreground">
              <span>Showing recent 5 records</span>
            </div>
          </CardFooter>
        </Card>
      </div>
    </div>
  )
}
 