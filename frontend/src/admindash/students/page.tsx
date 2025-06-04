"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { getStudents, getClasses, addStudent, updateStudent, deleteStudent } from "@/lib/api"
import type { Student, Class } from "@/lib/types"

export default function StudentsPage() {
  const [students, setStudents] = useState<Student[]>([])
  const [classes, setClasses] = useState<Class[]>([])
  const [searchTerm, setSearchTerm] = useState("")
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false)
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false)
  const [currentStudent, setCurrentStudent] = useState<Student | null>(null)

  useEffect(() => {
    async function fetchData() {
      try {
        const studentsData = await getStudents()
        const classesData = await getClasses()
        setStudents(studentsData)
        setClasses(classesData)
      } catch (error) {
        console.error("Error fetching data:", error)
      }
    }
    fetchData()
  }, [])

  const filteredStudents = students.filter(
    (student) =>
      student.first_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      student.last_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      student.user.username.toLowerCase().includes(searchTerm.toLowerCase()),
  )

  const handleAddStudent = (newStudent: Omit<Student, "user">) => {
    const addedStudent = addStudent(newStudent)
    setStudents([...students, addedStudent])
    setIsAddDialogOpen(false)
  }

  const handleUpdateStudent = (updatedStudent: Student) => {
    const updated = updateStudent(updatedStudent)
    setStudents(students.map((s) => (s.user.id === updated.user.id ? updated : s)))
    setIsEditDialogOpen(false)
  }

  const handleDeleteStudent = (userId: number) => {
    deleteStudent(userId)
    setStudents(students.filter((s) => s.user.id !== userId))
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Students</h1>
        <Dialog open={isAddDialogOpen} onOpenChange={setIsAddDialogOpen}>
          <DialogTrigger asChild>
            <Button>Add New Student</Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Add New Student</DialogTitle>
            </DialogHeader>
            <StudentForm onSubmit={handleAddStudent} classes={classes} />
          </DialogContent>
        </Dialog>
      </div>
      <div className="flex justify-between items-center">
        <Input
          placeholder="Search students..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="max-w-sm"
        />
      </div>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Name</TableHead>
            <TableHead>Username</TableHead>
            <TableHead>Class</TableHead>
            <TableHead>Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {filteredStudents.map((student) => (
            <TableRow key={student.user.id}>
              <TableCell>{`${student.first_name} ${student.middle_name || ""} ${student.last_name}`}</TableCell>
              <TableCell>{student.user.username}</TableCell>
              <TableCell>{student.student_class.name}</TableCell>
              <TableCell>
                <Dialog open={isEditDialogOpen} onOpenChange={setIsEditDialogOpen}>
                  <DialogTrigger asChild>
                    <Button variant="outline" className="mr-2" onClick={() => setCurrentStudent(student)}>
                      Edit
                    </Button>
                  </DialogTrigger>
                  <DialogContent>
                    <DialogHeader>
                      <DialogTitle>Edit Student</DialogTitle>
                    </DialogHeader>
                    {currentStudent && (
                      <StudentForm onSubmit={handleUpdateStudent} initialData={currentStudent} classes={classes} />
                    )}
                  </DialogContent>
                </Dialog>
                <Button variant="destructive" onClick={() => handleDeleteStudent(student.user.id)}>
                  Delete
                </Button>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  )
}

interface StudentFormProps {
  onSubmit: (studentData: Omit<Student, "user">) => void
  initialData?: Student
  classes: Class[]
}

function StudentForm({ onSubmit, initialData, classes }: StudentFormProps) {
  const [formData, setFormData] = useState<Omit<Student, "user">>(
    initialData || {
      first_name: "",
      middle_name: "",
      last_name: "",
      student_class: classes[0],
      student_img: "",
    },
  )

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSubmit(formData)
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setFormData((prev) => ({ ...prev, [name]: value }))
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <Label htmlFor="first_name">First Name</Label>
        <Input id="first_name" name="first_name" value={formData.first_name} onChange={handleChange} required />
      </div>
      <div>
        <Label htmlFor="middle_name">Middle Name</Label>
        <Input id="middle_name" name="middle_name" value={formData.middle_name} onChange={handleChange} />
      </div>
      <div>
        <Label htmlFor="last_name">Last Name</Label>
        <Input id="last_name" name="last_name" value={formData.last_name} onChange={handleChange} required />
      </div>
      <div>
        <Label htmlFor="student_class">Class</Label>
        <Select
          name="student_class"
          value={formData.student_class.class_id.toString()}
          onValueChange={(value) =>
            setFormData((prev) => ({
              ...prev,
              student_class: classes.find((c) => c.class_id === Number.parseInt(value)) || classes[0],
            }))
          }
        >
          <SelectTrigger>
            <SelectValue placeholder="Select class" />
          </SelectTrigger>
          <SelectContent>
            {classes.map((cls) => (
              <SelectItem key={cls.class_id} value={cls.class_id.toString()}>
                {cls.name} - {cls.section}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
      <div>
        <Label htmlFor="student_img">Profile Image URL</Label>
        <Input id="student_img" name="student_img" value={formData.student_img} onChange={handleChange} />
      </div>
      <Button type="submit">{initialData ? "Update" : "Add"} Student</Button>
    </form>
  )
}