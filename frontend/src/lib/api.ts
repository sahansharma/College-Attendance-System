import axios from "axios"
import type { Attendance, AttendanceReport, Class, Student } from "./types"

const API_BASE_URL = "http://localhost:8000/admin_app"

const api = axios.create({
    baseURL: API_BASE_URL,
    withCredentials: true,
})

// Classes
export const getClasses = async (): Promise<Class[]> => {
    const response = await api.get("/classes/")
    return response.data
}

export const addClass = async (classData: Omit<Class, "class_id">): Promise<Class> => {
    const response = await api.post("/classes/create/", classData)
    return response.data
}

export const updateClass = async (classData: Class): Promise<Class> => {
    const response = await api.put(`/classes/${classData.class_id}/`, classData)
    return response.data
}

export const deleteClass = async (classId: number): Promise<void> => {
    await api.delete(`/classes/${classId}/delete/`)
}

export const getClassCount = async (): Promise<number> => {
    const response = await api.get("/classes/count/")
    return response.data.total_classes
}

// Students
export const getStudents = async (): Promise<Student[]> => {
    const response = await api.get("/students/")
    return response.data
}

export const addStudent = async (studentData: Omit<Student, "user">): Promise<Student> => {
    const response = await api.post("/students/create/", studentData)
    return response.data
}

export const updateStudent = async (studentData: Student): Promise<Student> => {
    // Assuming student update uses user.id as the identifier
    const response = await api.put(`/students/${studentData.user.id}/`, studentData)
    return response.data
}

export const deleteStudent = async (userId: number): Promise<void> => {
    await api.delete(`/students/${userId}/delete/`)
}

export const getStudentCount = async (): Promise<number> => {
    const response = await api.get("/students/count/")
    return response.data.total_students
}

// Attendance
export const getAttendance = async (): Promise<Attendance[]> => {
    const response = await api.get("/attendance/")
    return response.data
}

export const updateAttendanceStatus = async (
    id: number,
    status: "Present" | "Absent" | "Late"
): Promise<Attendance> => {
    const response = await api.put(`/attendance/${id}/`, { status })
    return response.data
}

export const bulkUpdateAttendance = async (
    ids: number[],
    status: "Present" | "Absent" | "Late"
): Promise<Attendance[]> => {
    // Since the backend bulk-update endpoint is commented out, we simulate it
    const updates = ids.map((id) => updateAttendanceStatus(id, status))
    return Promise.all(updates)
}

export const getRecentAttendance = async (): Promise<Attendance[]> => {
    const response = await api.get("/attendance/recent/")
    return response.data
}

export const getAttendanceTrend = async (): Promise<any[]> => {
    const response = await api.get("/attendance/trend/")
    return response.data
}

// Reports
export const getAttendanceReport = async (
    classId: string,
    startDate: Date,
    endDate: Date
): Promise<AttendanceReport> => {
    const response = await api.post("/reports/attendance/", {
        classId: parseInt(classId),
        startDate: startDate.toISOString().split("T")[0],
        endDate: endDate.toISOString().split("T")[0],
    })
    return response.data
}

export const exportAttendanceReport = async (
    classId: string,
    startDate: Date,
    endDate: Date
): Promise<void> => {
    const response = await api.post(
        "/reports/export/",
        {
            classId: parseInt(classId),
            startDate: startDate.toISOString().split("T")[0],
            endDate: endDate.toISOString().split("T")[0],
        },
        { responseType: "blob" }
    )

    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement("a")
    link.href = url
    link.setAttribute("download", `attendance_report_${classId}.csv`)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
}

export default api
