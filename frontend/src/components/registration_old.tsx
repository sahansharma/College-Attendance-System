// 'use client'

import { useRef, useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Camera, AlertCircle } from 'lucide-react'

import { useNavigate } from "react-router-dom";
import axios from "axios";
import { toast } from "react-toastify";
// import CountryInput from "../components/CountryInput";
import { useEffect } from "react";

export default function RegistrationForm() {
  const videoRef = useRef<HTMLVideoElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const [stream, setStream] = useState<MediaStream | null>(null)
  const [showCamera, setShowCamera] = useState(false)
  const [error, setError] = useState<string>('')
  const [faceImage, setFaceImage] = useState<string | null>(null)
  const [successMessage, setSuccessMessage] = useState<string>('')

  const startCamera = async () => {
    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'user' }
      })
      setStream(mediaStream)
      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream
      }
      setError('')
    } catch (err) {
      setError('Unable to access camera. Please ensure you have granted camera permissions.'+err)
    }
  }


const URL = "https://localhost:8000/api/register";
const Register = (props) => {
  const { isLoggedIn, setIsLoggedIn, setName, setEmail } = props;
  let navigate = useNavigate();

  useEffect(() => {
    if (isLoggedIn) navigate("dashboard");
  });

  const handleRegister = async (ev) => {
    ev.preventDefault();
    const name = ev.target.name.value;
    const email = ev.target.email.value;
    const password = ev.target.password.value;
    const confirmpassword = ev.target.confirmpassword.value;
    const country = ev.target.country.value;
    const phone = ev.target.phone.value;
    if (country === "Select Country") toast.error("Select your country !");
    if (password !== confirmpassword) toast.error("Passwords do not match !");
    else{
      const formData = {
        name: name,
        email: email,
        password: password,
        country: country,
        phone: phone,
      };
      try {
        const res = await axios.post(URL, formData);
        const data = res.data;
        if (data.success === true) {
          toast.success(data.message);
          setIsLoggedIn(true);
          setName(name);
          setEmail(email);
          navigate("/dashboard");
        } else {
          toast.error(data.message);
        }
      } catch (err) {
        console.log("Some error occured", err);
      }
    }
  };



  const stopCamera = () => {
    if (stream) {
      stream.getTracks().forEach(track => track.stop())
      setStream(null)
    }
  }

  const capturePhoto = () => {
    if (videoRef.current && canvasRef.current) {
      const video = videoRef.current
      const canvas = canvasRef.current
      const context = canvas.getContext('2d')

      if (context) {
        canvas.width = video.videoWidth
        canvas.height = video.videoHeight
        context.drawImage(video, 0, 0, canvas.width, canvas.height)
        const imageData = canvas.toDataURL('image/jpeg')
        setFaceImage(imageData)
        stopCamera()
        setShowCamera(false)
        setSuccessMessage('Photo captured successfully!')
        setTimeout(() => setSuccessMessage(''), 3000)
      }
    }
  }

  const handleSubmit_old = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!faceImage) {
      setError('Please capture your face photo before submitting.')
      return
    }

    // Here you would typically send both form data and face image to your backend 
    const formData = new FormData(e.target as HTMLFormElement)
    formData.append('faceImage', faceImage)
    
    // Simulating API call
    console.log('Submitting registration with face data:', {
      formData: Object.fromEntries(formData),
      faceImageLength: faceImage.length
    })

    setSuccessMessage('Registration completed successfully!')
    setTimeout(() => setSuccessMessage(''), 3000)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!faceImage) {
      setError('Please capture your face photo before submitting.');
      return;
    }
    const form = e.target as HTMLFormElement;
    const name = form.firstname.value;
    const email = form.target.email.value;
    const password = form.password.value;
    const confirmpassword = form.confirmpassword.value;
    const country = form.country.value;
    const phone = form.phone.value;
  
    if (country === "Select Country") toast.error("Select your country !");
    if (password !== confirmpassword) toast.error("Passwords do not match !");
  
    const formData = new FormData(e.target as HTMLFormElement);
    formData.append('faceImage', faceImage);
  
    try {
      const res = await axios.post(URL, {
        name: name,
        email: email,
        password: password,
        country: country,
        phone: phone,
        faceImage: faceImage,
      });
      const data = res.data;
      if (data.success === true) {
        toast.success(data.message);
        setIsLoggedIn(true);
        setName(name);
        setEmail(email);
        navigate("/profile");
      } else {
        toast.error(data.message);
      }
    } catch (err) {
      console.log("Some error occured", err);
    }
  };

  return (
    <>
    <div className="min-h-screen flex items-center justify-center p-4">
      <Card className="w-full max-w-2xl">
        <CardHeader>
          <CardTitle>Student Registration</CardTitle>
          <CardDescription>
            Please fill in your details and capture your face photo to create a new student account
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
            <div className="space-y-4">
              <h3 className="text-lg font-medium">Personal Information</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="firstname">First Name</Label>
                  <Input id="firstname" name="firstname" placeholder="John" required />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="middlename">Middle Name</Label>
                  <Input id="middlename" name="middlename" placeholder="David" />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="lastname">Last Name</Label>
                  <Input id="lastname" name="lastname" placeholder="Smith" required />
                </div>
              </div>
            </div>

            {/* Academic Information */}
            <div className="space-y-4">
              <h3 className="text-lg font-medium">Academic Information</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="class">Class</Label>
                  <Select name="class">
                    <SelectTrigger>
                      <SelectValue placeholder="Select class" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="1">Class 1</SelectItem>
                      <SelectItem value="2">Class 2</SelectItem>
                      <SelectItem value="3">Class 3</SelectItem>
                      <SelectItem value="4">Class 4</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="section">Section</Label>
                  <Select name="section">
                    <SelectTrigger>
                      <SelectValue placeholder="Select section" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="A">Section A</SelectItem>
                      <SelectItem value="B">Section B</SelectItem>
                      <SelectItem value="C">Section C</SelectItem>
                      <SelectItem value="D">Section D</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="year">Year</Label>
                  <Select name="year">
                    <SelectTrigger>
                      <SelectValue placeholder="Select year" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="2024">2024</SelectItem>
                      <SelectItem value="2025">2025</SelectItem>
                      <SelectItem value="2026">2026</SelectItem>
                      <SelectItem value="2027">2027</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </div>

            {/* Account Information */}
            <div className="space-y-4">
              <h3 className="text-lg font-medium">Account Information</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="username">Username</Label>
                  <Input id="username" name="username" placeholder="johnsmith123" required />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="password">Password</Label>
                  <Input 
                    id="password" 
                    name="password"
                    type="password" 
                    required
                    minLength={8}
                  />
                  <p className="text-sm text-muted-foreground">
                    Password must be at least 8 characters long
                  </p>
                </div>
              </div>
            </div>

            {/* Face Enrollment Section */}
            <div className="space-y-4">
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
                    <video
                      ref={videoRef}
                      autoPlay
                      playsInline
                      muted
                      className="w-full h-full object-cover"
                    />
                  </div>
                  <div className="flex justify-center gap-4">
                    <Button type="button" variant="outline" onClick={() => {
                      stopCamera()
                      setShowCamera(false)
                    }}>
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
                          src={faceImage || "/placeholder.svg"} 
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
                      className="w-full"
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

            {/* Submit Button */}
            <Button type="submit" className="w-full">
              Complete Registration
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
    </>
  )
}
}