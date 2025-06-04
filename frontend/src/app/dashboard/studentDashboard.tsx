"use client"
import { useState, useEffect, useRef, useCallback } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { getStudentDashboard } from '@/services/ApiServices';
import { logout } from "@/services/ApiServices";
import {
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts"
import { Button } from "@/components/ui/button"
import { Camera, Check, Loader2, RefreshCw, LogOut, Download } from "lucide-react"

import { useToast } from "@/hooks/use-toast"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog"
import axios from 'axios';
import Header from "@/components/header"

// const studentData = await getStudentDashboard(34);

const COLORS = ["#0088FE", "#00C49F", "#FFBB28"]

interface StudentData {
  student_img: string;
  first_name: string;
  middle_name: string;
  last_name: string;
  student_class: {
    name: string;
    section: string;
    semester: string;
    year: string;
  };
  last_check_in: string;
  attendance: {
    overall_percentage: number;
    total_present: number;
    total_absent: number;
    total_late: number;
    breakdown: { name: string; value: number }[];
  };
  class_ranking: {
    rank: number;
    total: number;
  };
  recent_attendance: { date: string; status: string }[];
  attendance_trend: { date: string; attendance: number }[];
}

export default function StudentDashboard(props: any) {
  const [studentData, setStudentData] = useState<StudentData | null>(null);
  const [loading, setLoading] = useState(true);
  const [isChecking, setIsChecking] = useState(false)
  const [isVerified, setIsVerified] = useState(false)
  const [isCameraOpen, setIsCameraOpen] = useState(false)
  const [capturedImage, setCapturedImage] = useState<string | null>(null)
  const [isWithinCollegeRadius, setIsWithinCollegeRadius] = useState(false)
  const videoRef = useRef<HTMLVideoElement>(null)
  const { toast } = useToast()

  // NCC College Coordinates (27.71477743675058, 85.30895279815599)
  const collegeLatitude = 27.71477743675058; // college's latitude
  const collegeLongitude = 85.30895279815599; //  college's longitude

  // Test coordinates for distance calculation 27.657877442484125, 85.31549198661901
  // const collegeLatitude = 27.657877442484125; 
  // const collegeLongitude = 85.31549198661901; 
  const allowedRadius = 100; // allowed radius in meters
  


  useEffect(() => {
    if (studentData) {
      setIsVerified(new Date(studentData.last_check_in).toDateString() === new Date().toDateString());
      console.log(new Date(studentData.last_check_in).toDateString())
      console.log("Date:", new Date().toDateString())
    }
  }, [studentData]);

  // useEffect(() => {
  //   if (navigator.geolocation) {
  //     navigator.geolocation.getCurrentPosition(
  //       (position) => {
  //         const { latitude, longitude } = position.coords;
  //         const distance = getDistanceFromLatLonInMeters(latitude, longitude, collegeLatitude, collegeLongitude);
  //         console.log("Distance from college:", distance);
  //         setIsWithinCollegeRadius(distance <= allowedRadius);
  //         if (distance > allowedRadius) {
  //           toast({
  //             title: "Out of College Radius",
  //             description: "You are not within the college radius. Attendance check-in is disabled.",
  //             variant: "destructive",
  //           });
  //         }
  //       },
  //       (error) => {
  //         console.error("Error getting location", error);
  //         toast({
  //           title: "Location Error",
  //           description: "Unable to access your location. Please check your permissions.",
  //           variant: "destructive",
  //         });
  //       }
  //     );
  //   } else {
  //     toast({
  //       title: "Geolocation Error",
  //       description: "Geolocation is not supported by your browser.",
  //       variant: "destructive",
  //     });
  //   }
  // }, [toast]);

  const getDistanceFromLatLonInMeters = (lat1, lon1, lat2, lon2) => {
    const R = 6371e3; // Radius of the earth in meters
    const dLat = deg2rad(lat2 - lat1);
    const dLon = deg2rad(lon2 - lon1);
    const a =
      Math.sin(dLat / 2) * Math.sin(dLat / 2) +
      Math.cos(deg2rad(lat1)) * Math.cos(deg2rad(lat2)) *
      Math.sin(dLon / 2) * Math.sin(dLon / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    const distance = R * c; // Distance in meters
    return distance;
  };

  const deg2rad = (deg) => {
    return deg * (Math.PI / 180);
  };

  const closeCamera = useCallback(() => {
    if (videoRef.current) {
        const stream = videoRef.current.srcObject as MediaStream;
        if (stream) {
            stream.getTracks().forEach((track) => {
                track.stop(); // Stop each track properly
                console.log(`Stopped track: ${track.kind}`);
            });
            videoRef.current.srcObject = null; // Clear the stream reference
            console.log("Camera closed and video source set to null");
        }
    }
    //setIsCameraOpen(false);
    // setCapturedImage(null);
}, []);

const openCamera = useCallback(async () => {
    closeCamera(); // Ensure any existing camera stream is closed before opening a new one
    setIsCameraOpen(true);

    try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        if (videoRef.current) {
            videoRef.current.srcObject = stream;
        }
    } catch (err) {
        console.error("Error accessing the camera", err);
        toast({
            title: "Camera Error",
            description: "Unable to access the camera. Please check your permissions.",
            variant: "destructive",
        });
        closeCamera(); // Ensure the camera is closed in case of an error
    }
}, [closeCamera, toast]);

const capturePhoto = useCallback(() => {
    if (videoRef.current) {
        const canvas = document.createElement("canvas");
        canvas.width = videoRef.current.videoWidth;
        canvas.height = videoRef.current.videoHeight;
        canvas.getContext("2d")?.drawImage(videoRef.current, 0, 0);
        const imageDataUrl = canvas.toDataURL("image/jpeg");
        setCapturedImage(imageDataUrl);
        closeCamera();
    }
}, []);

const retakePhoto = useCallback(() => {
    setCapturedImage(null);
    openCamera();
}, []);

const handleAttendance = useCallback(async () => {
    setIsChecking(true);

    if (!capturedImage) {
        toast({
            title: "No Image Captured",
            description: "Please capture an image before proceeding.",
            variant: "destructive",
        });
        setIsChecking(false);
        return;
    }

    const imageData = capturedImage.split(',')[1];
    console.log("Captured image data:", imageData);

    try {
        const response = await axios.post(
            'http://localhost:8000/api/face-verification',
            {
                student_id: props.id,
                image_data: imageData,
            }
        );
        console.log("Verification response:", response.data);
        setIsVerified(response.data.verified);
        closeCamera();
        setIsCameraOpen(false);
        setCapturedImage(null);
        
        toast({
            title: response.data.verified ? "Attendance Verified" : "Attendance Not Verified",
            description: response.data.verified
                ? "Your attendance has been recorded for today."
                : "Face does not match. Please try again.",
            variant: response.data.verified ? "default" : "destructive",
            className: response.data.verified ? "bg-green-500" : "bg-red-500",
        });
    } catch (error) {
        console.error("Error verifying attendance", error);
        closeCamera();
        setIsCameraOpen(false);
        setCapturedImage(null);
        toast({
            title: "Attendance Error",
            description: "An error occurred while verifying your attendance. Please try again.",
            variant: "destructive",
        });
    } finally {
        setIsChecking(false);
        setIsCameraOpen(false);
        setCapturedImage(null);
        closeCamera(); // Ensure camera is closed after verification
    }
}, [capturedImage, props.id, closeCamera, toast]);

const handleLogout = useCallback(async () => {
    try {
        await logout();
        toast({
            title: "Logged Out",
            description: "You have been successfully logged out.",
            className: "bg-green-500",
        });
        window.location.href = "/login"; // OR use Next.js router
    } catch (error) {
        console.error("Logout failed", error);
        toast({
            title: "Logout Error",
            description: "An error occurred while logging out.",
            variant: "destructive",
        });
    }
}, [toast]);

  

  const handleDownloadReport = useCallback(() => {
    // Import jsPDF
    import("jspdf").then(async jsPDF => {
      const autoTable = (await import("jspdf-autotable")).default;
      const doc = new jsPDF.default();

      // Add title
      doc.setFontSize(18);
      doc.text("Student Attendance Report", 14, 22);

      // Add student information
      doc.setFontSize(12);
      if(studentData){
        doc.text(`Name: ${studentData.first_name} ${studentData.middle_name} ${studentData.last_name}`, 14, 32);
        doc.text(`Class: ${studentData.student_class.name} - Section ${studentData.student_class.section}`, 14, 40);
        doc.text(`Semester: ${studentData.student_class.semester} ${studentData.student_class.year}`, 14, 48);
        doc.text(`Overall Attendance: ${studentData.attendance.overall_percentage}%`, 14, 56);
        doc.text(`Class Rank: ${studentData.class_ranking.rank}/${studentData.class_ranking.total}`, 14, 64);

        // Add recent attendance records
        doc.text("Recent Attendance Records:", 14, 74);
        const tableColumn = ["Date", "Status"];
        const tableRows = studentData.recent_attendance.map(record => [record.date, record.status]);

        // Add table
        autoTable(doc, {
          startY: 80,
          head: [tableColumn],
          body: tableRows,
        });

        // Save the PDF
        doc.save(`attendance_report_${studentData.first_name}_${studentData.last_name}.pdf`);
      }
      
      toast({
        title: "Report Downloaded",
        description: "Your attendance report has been downloaded.",
        className: "bg-green-500",
      });
    });
  }, [studentData, toast]);

  const id = props.id;

  useEffect(() => {
    const fetchStudentData = async () => {
      if (!id) return; // Conditional logic inside useEffect, not before Hooks

      setLoading(true);
      try {
        console.log("Fetching data for ID:", id);
        const data = await getStudentDashboard(id);
        setStudentData(data);
      } catch (error) {
        console.error("Error fetching student data:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchStudentData();
  }, [id]); // Only re-run when `id` changes

  //Conditional UI rendering (outside of Hook logic)
  if (!id) return <p>No ID provided</p>;
  if (loading) return <p>Loading...</p>;
  if (!studentData) return <p>No student data available.</p>;

  console.log("studentData", studentData);

  


  return (
    <div className="container mx-auto p-4">
      {/* 1. Student Profile Summary */}
      <Card className="mb-8">
        <CardContent className="flex items-center justify-between pt-6">
          <div className="flex items-center space-x-4">
            <Avatar className="h-24 w-24">
              <AvatarImage src={studentData.student_img} alt={`${studentData.first_name} ${studentData.last_name}`} />
              <AvatarFallback>
                {studentData.first_name[0]}
                {studentData.last_name[0]}
              </AvatarFallback>
            </Avatar>
            <div>
              <h2 className="text-2xl font-bold">{`${studentData.first_name} ${studentData.middle_name} ${studentData.last_name}`}</h2>
              <p className="text-muted-foreground">{`${studentData.student_class.name} - Section ${studentData.student_class.section}`}</p>
              <p className="text-muted-foreground">{`${studentData.student_class.semester} ${studentData.student_class.year}`}</p>
            </div>
          </div>
          <div className="flex space-x-2">
            <Button onClick={handleDownloadReport}>
              <Download className="mr-2 h-4 w-4" />
              Download Report
            </Button>
            <Button onClick={handleLogout} variant="outline">
              <LogOut className="mr-2 h-4 w-4" />
              Logout
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Attendance Check-In Card */}
      <Card className="mb-8">
        <CardHeader>
          <CardTitle>Today's Attendance</CardTitle>
        </CardHeader>
        <CardContent className="flex items-center justify-between">
          <p className="text-sm text-muted-foreground">
        {isVerified ? `Last check-in: ${studentData.last_check_in}` : "Please verify your attendance for today."}
          </p>
          <Button
        onClick={openCamera}
        disabled={
          //isChecking || //PRODUCTION
          //isVerified ||
          //new Date(studentData.last_check_in).toDateString() === new Date().toDateString() ||
          //!isWithinCollegeRadius
          false //TESTING
        }
          >
        {isVerified ? (
          <>
            <Check className="mr-2 h-4 w-4" />
            Verified
          </>
        ) : (
          <>
            <Camera className="mr-2 h-4 w-4" />
            Take Attendance
          </>
        )}
          </Button>
        </CardContent>
      </Card>

      {/* 2. Attendance Overview */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3 mb-8">
        <Card>
          <CardHeader>
            <CardTitle>Overall Attendance</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-4xl font-bold">{studentData.attendance.overall_percentage}%</div>
            <p className="text-muted-foreground">
              Total Classes:{" "}
              {studentData.attendance.total_present +
                studentData.attendance.total_absent +
                studentData.attendance.total_late}
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Attendance Breakdown</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={200}>
              <PieChart>
                <Pie
                  data={studentData.attendance.breakdown}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {studentData.attendance.breakdown.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Class Ranking</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-4xl font-bold">Rank: {studentData.class_ranking.rank}
            {(() => {
              const rank = studentData.class_ranking.rank;
              const suffix = (rank) => {
                const j = rank % 10,
                  k = rank % 100;
                if (j === 1 && k !== 11) {
                  return "st";
                }
                if (j === 2 && k !== 12) {
                  return "nd";
                }
                if (j === 3 && k !== 13) {
                  return "rd";
                }
                return "th";
              };
              return <sup>{suffix(rank)}</sup>;
            })()}</div>
            <p className="text-muted-foreground">Total Students: {studentData.class_ranking.total}</p>
          </CardContent>
        </Card>
      </div>

      {/* 3. Recent Attendance Records */}
      <Card className="mb-8">
        <CardHeader>
          <CardTitle>Recent Attendance Records</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Date</TableHead>
                <TableHead>Status</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {studentData.recent_attendance.map((record, index) => (
                <TableRow key={index}>
                  <TableCell>{record.date}</TableCell>
                  <TableCell>{record.status}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* 4. Attendance Trend */}
      <Card>
        <CardHeader>
          <CardTitle>Attendance Trend (Last 7 Days)</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={studentData.attendance_trend}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis 
              tickFormatter={(value) => {
                switch (value) {
                case 1:
                  return 'Present';
                case 0:
                  return 'Absent';
                case 0.5:
                  return 'Late';
                default:
                  return '';
                }
              }}
              />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="attendance" stroke="#8884d8" activeDot={{ r: 8 }} />
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Camera Dialog */}
      <Dialog open={isCameraOpen} onOpenChange={setIsCameraOpen}>
        <DialogContent className="sm:max-w-[425px]">
          <DialogHeader>
            <DialogTitle>Attendance Check-In</DialogTitle>
            <DialogDescription>Please ensure your face is clearly visible in the camera.</DialogDescription>
          </DialogHeader>
          <div className="mt-4">
            {!capturedImage ? (
              <div className="relative aspect-video">
                <video ref={videoRef} autoPlay playsInline muted className="w-full h-full object-cover rounded-md" />
              </div>
            ) : (
              <div className="relative aspect-video">
                <img
                  src={capturedImage || "/placeholder.svg"}
                  alt="Captured"
                  className="w-full h-full object-cover rounded-md"
                />
              
              </div>
            )}
          </div>
          <DialogFooter className="sm:justify-start">
            {!capturedImage ? (
              <Button onClick={capturePhoto}>
                <Camera className="mr-2 h-4 w-4" />
                Capture
              </Button>
            ) : (
              <>
                <Button onClick={retakePhoto} variant="outline">
                  <RefreshCw className="mr-2 h-4 w-4" />
                  Retake
                </Button>
                <Button onClick={handleAttendance} disabled={isChecking}>
                  {isChecking ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Verifying...
                    </>
                  ) : (
                    <>
                      <Check className="mr-2 h-4 w-4" />
                      Submit for Verification
                    </>
                  )}
                </Button>
              </>
            )}
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
