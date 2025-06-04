"use client"

import { useState, useEffect } from "react"
import { format } from "date-fns"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { DatePicker } from "@/components/ui/date-picker"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { getAttendanceReport, exportAttendanceReport, getClasses } from "@/lib/api"
import { FileDown } from "lucide-react"
import type { Class, AttendanceReport } from "@/lib/types"

const ClassSelector = ({
  classes,
  selectedClass,
  setSelectedClass,
}: {
  classes: Class[]
  selectedClass: string
  setSelectedClass: (value: string) => void
}) => (
  <Select value={selectedClass} onValueChange={setSelectedClass}>
    <SelectTrigger className="w-[300px]">
      <SelectValue placeholder="Select Class" />
    </SelectTrigger>
    <SelectContent>
      {classes.map((cls) => (
        <SelectItem key={cls.class_id} value={String(cls.class_id)}>
          {cls.name} - {cls.section} (Semester {cls.semester}, {cls.year})
        </SelectItem>
      ))}
    </SelectContent>
  </Select>
)

export default function ReportsPage() {
  const [classes, setClasses] = useState<Class[]>([])
  const [selectedClass, setSelectedClass] = useState<string>("")
  const [startDate, setStartDate] = useState<Date>(new Date())
  const [endDate, setEndDate] = useState<Date>(new Date())
  const [reportData, setReportData] = useState<AttendanceReport | null>(null)

  useEffect(() => {
    const loadClasses = async () => {
      const data = await getClasses()
      setClasses(data)
    }
    loadClasses()
  }, [])

  const handleGenerateReport = async () => {
    if (!selectedClass) return
    const report = await getAttendanceReport(selectedClass, startDate, endDate)
    setReportData(report)
  }

  const handleExportReport = async () => {
    if (!selectedClass) return
    await exportAttendanceReport(selectedClass, startDate, endDate)
  }

  const selectedClassObj = classes.find(c => String(c.class_id) === selectedClass)

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-3xl font-bold">Attendance Reports</h1>

      <Card>
        <CardHeader>
          <CardTitle>Generate Report</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex flex-col md:flex-row gap-4">
            <ClassSelector classes={classes} selectedClass={selectedClass} setSelectedClass={setSelectedClass} />
            <div className="flex flex-col md:flex-row gap-4">
              <DatePicker 
                selected={startDate} 
                onSelect={(date) => date && setStartDate(date)} 
                placeholder="Start Date"
                className="w-full"
              />
              <DatePicker 
                selected={endDate} 
                onSelect={(date) => date && setEndDate(date)} 
                placeholder="End Date"
                className="w-full"
              />
            </div>
          </div>
          <div className="flex flex-col md:flex-row gap-4">
            <Button onClick={handleGenerateReport}>Generate Report</Button>
            <Button variant="outline" onClick={handleExportReport}>
              <FileDown className="mr-2 h-4 w-4" />
              Export Report
            </Button>
          </div>
        </CardContent>
      </Card>

      {reportData && selectedClassObj && (
        <Card>
          <CardHeader>
            <CardTitle>Attendance Report</CardTitle>
            <p className="text-sm text-muted-foreground">
              {selectedClassObj.name} - {selectedClassObj.section} 
              (Semester {selectedClassObj.semester}, {selectedClassObj.year})<br />
              From {format(startDate, 'MMM dd, yyyy')} to {format(endDate, 'MMM dd, yyyy')}
            </p>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              <div>
                <p className="text-sm text-muted-foreground">Total Days</p>
                <p className="text-2xl font-bold">{reportData.summary.totalDays}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Total Students</p>
                <p className="text-2xl font-bold">{reportData.summary.totalStudents}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Overall Attendance</p>
                <p className="text-2xl font-bold">{reportData.summary.overallAttendanceRate}%</p>
              </div>
            </div>

            <div className="grid grid-cols-3 gap-4">
              <div className="bg-green-100 p-4 rounded-lg">
                <p className="text-sm text-green-800">Present</p>
                <p className="text-2xl font-bold text-green-800">{reportData.summary.totalPresent}</p>
              </div>
              <div className="bg-yellow-100 p-4 rounded-lg">
                <p className="text-sm text-yellow-800">Late</p>
                <p className="text-2xl font-bold text-yellow-800">{reportData.summary.totalLate}</p>
              </div>
              <div className="bg-red-100 p-4 rounded-lg">
                <p className="text-sm text-red-800">Absent</p>
                <p className="text-2xl font-bold text-red-800">{reportData.summary.totalAbsent}</p>
              </div>
            </div>

            <h3 className="text-xl font-semibold">Student Attendance</h3>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Student</TableHead>
                  <TableHead className="text-center">Present</TableHead>
                  <TableHead className="text-center">Late</TableHead>
                  <TableHead className="text-center">Absent</TableHead>
                  <TableHead className="text-center">Attendance Rate</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {reportData.students.map((student) => (
                  <TableRow key={student.id}>
                    <TableCell>{student.name}</TableCell>
                    <TableCell className="text-center">{student.present}</TableCell>
                    <TableCell className="text-center">{student.late}</TableCell>
                    <TableCell className="text-center">{student.absent}</TableCell>
                    <TableCell className="text-center">{student.attendanceRate}%</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      )}
    </div>
  )
}