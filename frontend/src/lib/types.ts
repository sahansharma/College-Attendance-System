export interface User {
    id: number
    name: string
    username: string
}

export interface Admin {
    user: User
    role: { id: number; name: string }
    first_name: string
    last_name: string
}

export interface Class {
    class_id: number
    name: string
    section: string
    semester: string
    year: number
    admin: number | Admin
}

export interface Student {
    user: User
    first_name: string
    middle_name?: string
    last_name: string
    student_class: Class
    student_img?: string
}

export interface Attendance {
    id: number
    student: Student
    status: "Present" | "Absent" | "Late"
    date: string
}

export interface AttendanceReport {
    summary: {
        totalDays: number
        totalStudents: number
        totalPresent: number
        totalLate: number
        totalAbsent: number
        overallAttendanceRate: number
    }
    dailyBreakdown: {
        date: string
        present: number
        late: number
        absent: number
        attendanceRate: number
    }[]
    students: {
        id: number
        name: string
        present: number
        late: number
        absent: number
        attendanceRate: number
    }[]
}
