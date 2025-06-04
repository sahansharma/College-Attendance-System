"use client"

import { useRef, useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Camera, AlertCircle, Loader2 } from "lucide-react"
import { registerStudent } from "@/services/register-api"
import { toast } from "react-toastify"
import { useNavigate } from "react-router-dom"


export default function RegistrationForm() {
  const videoRef = useRef<HTMLVideoElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const [stream, setStream] = useState<MediaStream | null>(null)
  const [showCamera, setShowCamera] = useState(false)
  const [error, setError] = useState<string>("")
  const [faceImage, setFaceImage] = useState<string | null>(null)
  const [successMessage, setSuccessMessage] = useState<string>("")
  const [isLoading, setIsLoading] = useState(false)
  const navigate = useNavigate()

  const startCamera = async () => {
    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: "user" },
      })
      setStream(mediaStream)
      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream
      }
      setError("")
    } catch (err) {
      setError("Unable to access camera. Please ensure you have granted camera permissions.")
    }
  }

  const stopCamera = () => {
    if (stream) {
      stream.getTracks().forEach((track) => track.stop())
      setStream(null)
    }
  }

  const capturePhoto = () => {
    if (videoRef.current && canvasRef.current) {
      const video = videoRef.current
      const canvas = canvasRef.current
      const context = canvas.getContext("2d")

      if (context) {
        canvas.width = video.videoWidth
        canvas.height = video.videoHeight
        context.drawImage(video, 0, 0, canvas.width, canvas.height)
        const imageData = canvas.toDataURL("image/jpeg")
        setFaceImage(imageData)
        stopCamera()
        setShowCamera(false)
        setSuccessMessage("Photo captured successfully!")
        setTimeout(() => setSuccessMessage(""), 3000)
      }
    }
  }

  const validateForm = (formData: FormData) => {
    const firstName = formData.get("firstname") as string
    const middleName = formData.get("middlename") as string
    const lastName = formData.get("lastname") as string
    
    // Name validation
    if (!firstName || !/^[A-Za-z\s'-]{2,50}$/.test(firstName)) {
      return "First name must be 2-50 letters (spaces, hyphens, apostrophes allowed)"
    }

    if (middleName && !/^[A-Za-z\s'-]{0,50}$/.test(middleName)) {
      return "Middle name can only contain letters, spaces, hyphens, and apostrophes (max 50 characters)"
    }

    if (!lastName || !/^[A-Za-z\s'-]{2,50}$/.test(lastName)) {
      return "Last name must be 2-50 letters (spaces, hyphens, apostrophes allowed)"
    }

    // Account validation
    const username = formData.get("username") as string
    const password = formData.get("password") as string

    if (!username || !/^[a-zA-Z0-9_]{3,20}$/.test(username)) {
      return "Username must be 3-20 characters (letters, numbers, and underscores only)"
    }

    const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[\W_]).{8,}$/;

    if (!password || !passwordRegex.test(password)) {
      return "Password must be at least 8 characters long and include: 1 uppercase, 1 lowercase, 1 number, and 1 special character";
    }

    // Academic validation
    const studentClass = formData.get("class") as string
    const section = formData.get("section") as string
    const semester = formData.get("semester") as string
    const year = formData.get("year") as string

    if (!studentClass || !section || !semester || !year) {
      return "All academic fields are required"
    }

    const yearNumber = parseInt(year, 10)
    if (isNaN(yearNumber) || yearNumber < 2000 || yearNumber > new Date().getFullYear() + 1) {
      return "Please select a valid academic year"
    }

    return null
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError("")
    setSuccessMessage("")

    if (!faceImage) {
      setError("Please capture your face photo before submitting.")
      return
    }

    const formData = new FormData(e.target as HTMLFormElement)
    const validationError = validateForm(formData)
    if (validationError) {
      setError(validationError)
      return
    }

    try {
      setIsLoading(true)
      const registrationData = {
        username: formData.get("username") as string,
        password: formData.get("password") as string,
        first_name: formData.get("firstname") as string,
        middle_name: formData.get("middlename") as string,
        last_name: formData.get("lastname") as string,
        student_class: {
          name: formData.get("class") as string,
          section: formData.get("section") as string,
          semester: formData.get("semester") as string,
          year: Number(formData.get("year") as string),
        },
        student_img: faceImage,
      }

      const response = await registerStudent(registrationData)
      if (response.success) {
        setSuccessMessage("Registration completed successfully!")
        toast.success("Registration completed successfully!!")
        navigate("/login")
      } else {
        toast.error("Registration failed! Please try again.")
        setError(response.message)
      }
    } catch (err: any) {
      toast.error(err.response?.data?.detail || "An error occurred during registration.")
      setError("An unexpected error occurred. Please try again.")
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <>
      <div className="w-screen">
      </div>
      <div className="min-h-screen flex items-center justify-center p-4">
        <Card className="w-full max-w-2xl">
          <CardHeader>
            <CardTitle>Student Registration</CardTitle>
            <CardDescription>
              Please fill in your details and capture your face photo to register
            </CardDescription>
          </CardHeader>
          <CardContent>
            {successMessage && (
              <Alert className="mb-4 bg-green-50 text-green-700 border-green-200">
                <AlertDescription>{successMessage}</AlertDescription>
              </Alert>
            )}
            <form onSubmit={handleSubmit} className="space-y-8">
              {/* Personal Information */}
              <div className="space-y-4 rounded-xl border p-5">
                <h3 className="text-lg font-medium text-bold">Personal Information</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="firstname">First Name *</Label>
                    <Input id="firstname" name="firstname" placeholder="Ram" required />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="middlename">Middle Name</Label>
                    <Input id="middlename" name="middlename" placeholder="Prasad" />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="lastname">Last Name *</Label>
                    <Input id="lastname" name="lastname" placeholder="Thapa" required />
                  </div>
                </div>
              </div>

              {/* Academic Information */}
              <div className="space-y-4 rounded-xl border p-5">
                <h3 className="text-lg font-medium">Academic Information</h3>
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="class">Class *</Label>
                    <Select name="class" required>
                      <SelectTrigger>
                        <SelectValue placeholder="Select class" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="BIM">BIM</SelectItem>
                        <SelectItem value="BHM">BHM</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="semester">Semester *</Label>
                    <Select name="semester" required>
                      <SelectTrigger>
                        <SelectValue placeholder="Select semester" />
                      </SelectTrigger>
                      <SelectContent>
                        {["First", "Second", "Third", "Fourth", "Fifth", "Sixth", "Seventh", "Eighth"].map((sem) => (
                          <SelectItem key={sem} value={sem}>{sem}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="section">Section *</Label>
                    <Select name="section" required>
                      <SelectTrigger>
                        <SelectValue placeholder="Select section" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="A">A</SelectItem>
                        <SelectItem value="B">B</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="year">Year *</Label>
                    <Select name="year" required>
                      <SelectTrigger>
                        <SelectValue placeholder="Select year" />
                      </SelectTrigger>
                      <SelectContent>
                      <SelectItem value="2021">2021</SelectItem>
                      <SelectItem value="2022">2022</SelectItem>
                      <SelectItem value="2023">2023</SelectItem>
                      <SelectItem value="2024">2024</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
              </div>

              {/* Account Information */}
              <div className="space-y-4 rounded-xl border p-5">
                <h3 className="text-lg font-medium">Account Information</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="username">Username *</Label>
                    <Input 
                      id="username" 
                      name="username" 
                      placeholder="ramprasad123" 
                      required 
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="password">Password *</Label>
                    <Input 
                      id="password" 
                      name="password" 
                      type="password" 
                      required 
                      minLength={8}
                    />
                    <p className="text-sm text-muted-foreground">
                      Must include: uppercase, lowercase, number, special character
                    </p>
                  </div>
                </div>
              </div>

              {/* Face Enrollment Section */}
              <div className="space-y-4 rounded-xl border p-5">
                <h3 className="text-lg font-medium">Face Enrollment</h3>
                {error && (
                  <Alert variant="destructive">
                    <AlertCircle className="h-4 w-4" />
                    <AlertDescription>{error}</AlertDescription>
                  </Alert>
                )}

                {showCamera ? (
                  <div className="space-y-4">
                    <div className="relative w-full max-w-sm mx-auto aspect-video rounded-lg overflow-hidden bg-muted">
                      <video ref={videoRef} autoPlay playsInline muted className="w-full h-full object-cover" />
                    </div>
                    <div className="flex justify-center gap-4">
                      <Button
                        type="button"
                        variant="outline"
                        onClick={() => {
                          stopCamera()
                          setShowCamera(false)
                        }}
                      >
                        Cancel
                      </Button>
                      <Button type="button" onClick={capturePhoto}>
                        <Camera className="mr-2 h-4 w-4" />
                        Capture Photo
                      </Button>
                    </div>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {faceImage ? (
                      <div className="space-y-4">
                        <div className="relative w-full max-w-sm mx-auto aspect-video rounded-lg overflow-hidden bg-muted">
                          <img
                            src={faceImage}
                            alt="Captured face"
                            className="w-full h-full object-cover"
                          />
                        </div>
                        <Button
                          type="button"
                          variant="outline"
                          className="w-full"
                          onClick={() => {
                            setFaceImage(null)
                            setShowCamera(true)
                            startCamera()
                          }}
                        >
                          Retake Photo
                        </Button>
                      </div>
                    ) : (
                      <Button
                        type="button"
                        variant="outline"
                        className="w-60"
                        onClick={() => {
                          setShowCamera(true)
                          startCamera()
                        }}
                      >
                        <Camera className="mr-2 h-4 w-4" />
                        Start Camera
                      </Button>
                    )}
                  </div>
                )}
                <canvas ref={canvasRef} className="hidden" />
              </div>

              <Button type="submit" className="w-60" disabled={isLoading}>
                {isLoading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Registering...
                  </>
                ) : (
                  "Complete Registration"
                )}
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>
    </>
  )
}