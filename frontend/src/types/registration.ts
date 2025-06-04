export interface RegistrationFormData {
  firstName: string
  middleName: string
  lastName: string
  className: string
  section: string
  semester: string
  year: string
  faceImage: string | null
  username: string
  password: string
}

export interface ClassOption {
  value: string
  label: string
}

export const yearOptions: ClassOption[] = [
  { value: "1", label: "First Year" },
  { value: "2", label: "Second Year" },
  { value: "3", label: "Third Year" },
  { value: "4", label: "Fourth Year" },
]

export const semesterOptions: ClassOption[] = [
  { value: "1", label: "First Semester" },
  { value: "2", label: "Second Semester" },
]

export const sectionOptions: ClassOption[] = [
  { value: "A", label: "Section A" },
  { value: "B", label: "Section B" },
  { value: "C", label: "Section C" },
]

export const classOptions: ClassOption[] = [
  { value: "CSE", label: "Computer Science" },
  { value: "ECE", label: "Electronics" },
  { value: "ME", label: "Mechanical" },
  { value: "CE", label: "Civil" },
]

