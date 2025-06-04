"use client"

import { useState, useEffect } from "react"
import { Input } from "@/components/ui/input"
import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
} from "@/components/ui/table"
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from "@/components/ui/select"
import { DatePicker } from "@/components/ui/date-picker"
import {
  Card, CardContent, CardHeader, CardTitle,
} from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import {
  getAttendance, updateAttendanceStatus, getClasses, bulkUpdateAttendance,
} from "@/lib/api"
import type { Attendance, Class } from "@/lib/types"
import { BarChart, Calendar, Users } from "lucide-react"

export default function AttendancePage() {
  const [attendanceData, setAttendanceData] = useState<Attendance[]>([])
  const [classes, setClasses] = useState<Class[]>([])
  const [selectedClass, setSelectedClass] = useState<string>("all")
  const [selectedDate, setSelectedDate] = useState<Date>(new Date())
  const [searchTerm, setSearchTerm] = useState("")

  useEffect(() => {
    async function fetchData() {
      try {
        const [attendance, classList] = await Promise.all([getAttendance(), getClasses()])
        setAttendanceData(attendance)
        setClasses(classList)
      } catch (error) {
        console.error("Error fetching data:", error)
      }
    }
    fetchData()
  }, [])

  const filteredAttendance = attendanceData.filter((record) => {
    const isClassMatch =
      selectedClass === "all" || record.student.student_class.class_id.toString() === selectedClass
    const isDateMatch = record.date?.startsWith(selectedDate.toISOString().split("T")[0])
    const isSearchMatch =
      record.student.first_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      record.student.last_name.toLowerCase().includes(searchTerm.toLowerCase())
    return isClassMatch && isDateMatch && isSearchMatch
  })

  const attendanceStats = filteredAttendance.reduce(
    (acc, record) => {
      acc[record.status]++
      return acc
    },
    { Present: 0, Absent: 0, Late: 0 }
  )

  const attendanceRate =
    filteredAttendance.length > 0
      ? (((attendanceStats.Present + attendanceStats.Late) / filteredAttendance.length) * 100).toFixed(2)
      : "0.00"

  const handleStatusChange = async (id: number, status: "Present" | "Absent" | "Late") => {
    try {
      const updated = await updateAttendanceStatus(id, status)
      setAttendanceData((prev) =>
        prev.map((r) => (r.id === updated.id ? updated : r))
      )
    } catch (error) {
      console.error("Update failed:", error)
    }
  }

  const handleBulkUpdate = async (status: "Present" | "Absent" | "Late") => {
    try {
      const ids = filteredAttendance.map((r) => r.id)
      const updatedRecords = await bulkUpdateAttendance(ids, status)
      setAttendanceData((prev) =>
        prev.map((r) => updatedRecords.find((u) => u.id === r.id) || r)
      )
    } catch (error) {
      console.error("Bulk update failed:", error)
    }
  }

  return (
    <div className="p-6 space-y-6 w-full max-w-full bg-background text-foreground">
      <h1 className="text-3xl font-bold">Attendance Management</h1>

      {/* Stats cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Students</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{filteredAttendance.length}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Present</CardTitle>
            <Calendar className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{attendanceStats.Present}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Absent</CardTitle>
            <Calendar className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{attendanceStats.Absent}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Attendance Rate</CardTitle>
            <BarChart className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{attendanceRate}%</div>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap items-center gap-4">
        <Select value={selectedClass} onValueChange={setSelectedClass}>
          <SelectTrigger className="w-[200px]">
            <SelectValue placeholder="Select Class" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Classes</SelectItem>
            {classes.map((cls) => (
              <SelectItem key={cls.class_id} value={cls.class_id.toString()}>
                {cls.name} - {cls.section}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        <DatePicker selected={selectedDate} onSelect={(date) => date && setSelectedDate(date)} />

        <Input
          placeholder="Search student..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="max-w-sm"
        />
      </div>

      {/* Bulk update buttons */}
      <div className="flex flex-wrap gap-2">
        <Button onClick={() => handleBulkUpdate("Present")}>Mark All Present</Button>
        <Button onClick={() => handleBulkUpdate("Absent")} variant="destructive">
          Mark All Absent
        </Button>
        <Button onClick={() => handleBulkUpdate("Late")} variant="outline">
          Mark All Late
        </Button>
      </div>

      {/* Attendance Table */}
      <div className="overflow-x-auto">
        <Table className="w-full">
          <TableHeader>
            <TableRow>
              <TableHead>Student Name</TableHead>
              <TableHead>Class</TableHead>
              <TableHead>Date</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {filteredAttendance.map((record) => (
              <TableRow key={record.id}>
                <TableCell>{`${record.student.first_name} ${record.student.last_name}`}</TableCell>
                <TableCell>{`${record.student.student_class.name} - ${record.student.student_class.section}`}</TableCell>
                <TableCell>{new Date(record.date).toLocaleDateString()}</TableCell>
                <TableCell>{record.status}</TableCell>
                <TableCell>
                  <Select
                    value={record.status}
                    onValueChange={(value) => handleStatusChange(record.id, value as "Present" | "Absent" | "Late")}
                  >
                    <SelectTrigger className="w-[100px]">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="Present">Present</SelectItem>
                      <SelectItem value="Absent">Absent</SelectItem>
                      <SelectItem value="Late">Late</SelectItem>
                    </SelectContent>
                  </Select>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  )
}
