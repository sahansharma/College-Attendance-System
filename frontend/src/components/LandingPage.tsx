"use client"

import { Link } from "react-router-dom"
import { Button } from "@/components/ui/button"
import { UserCircle, ArrowRight, UserPlus, GraduationCap, Clock, ShieldCheck } from "lucide-react"

export default function LandingPage() {
  return (
    <>
      {/* Global styles to ensure full background coverage */}
      <style jsx global>{`
        html, body {
          margin: 0;
          padding: 0;
          background-color: #0f172a; /* slate-900 */
          height: 100%;
          width: 100%;
          overflow: hidden;
        }
      `}</style>

      <div className="fixed inset-0 w-screen h-screen flex items-center justify-center bg-slate-900">
        {/* Simple grid pattern overlay */}
        <div className="absolute inset-0 bg-grid-white/[0.02]"></div>

        {/* Main content */}
        <div className="container relative z-10 mx-auto px-4 flex flex-col md:flex-row items-center justify-between gap-8">
          {/* Left side - Content - Now center aligned */}
          <div className="w-full md:w-1/2 text-white space-y-6 flex flex-col items-center text-center">
            <div className="inline-flex items-center justify-center p-2 bg-blue-500/10 rounded-lg mb-2">
              <GraduationCap className="h-6 w-6 text-blue-400 mr-2" />
              <span className="text-sm font-medium text-blue-300">Nepal Commerce Campus</span>
            </div>

            <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold leading-tight">College Attendance System</h1>

            {/* Features centered */}
            <div className="flex flex-wrap justify-center gap-4">
              <div className="flex items-center">
                <Clock className="h-5 w-5 text-blue-400 mr-2" />
                <span className="text-gray-300">Save Time</span>
              </div>
              <div className="flex items-center">
                <ShieldCheck className="h-5 w-5 text-blue-400 mr-2" />
                <span className="text-gray-300">Enhanced Security</span>
              </div>
            </div>

            <p className="text-lg text-gray-300 max-w-xl">
              Streamline your college attendance tracking with our advanced facial recognition technology. Secure,
              efficient, and easy to use.
            </p>
          </div>

          {/* Right side - Buttons */}
          <div className="w-full md:w-2/5 bg-white/5 backdrop-blur-sm p-8 rounded-2xl border border-white/10 shadow-xl">
            <div className="flex justify-center mb-6">
              <div className="p-3 bg-blue-500/10 rounded-full">
                <UserCircle className="h-10 w-10 text-blue-400" />
              </div>
            </div>

            <h2 className="text-xl font-semibold text-white text-center mb-6">Access Your Account</h2>

            <div className="space-y-4">
              <Link to="/login/admin" className="w-full block">
                <Button
                  variant="default"
                  className="w-full py-6 text-base bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 border-0"
                >
                  Admin Login
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </Link>

              <Link to="/login" className="w-full block">
                <Button
                  variant="outline"
                  className="w-full py-6 text-base border-gray-700 bg-white/5 hover:bg-white/10 text-white"
                >
                  Student Login
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </Link>

              <Link to="/register" className="w-full block">
                <Button
                  variant="default"
                  className="w-full py-6 text-base bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 border-0"
                >
                  Register
                  <UserPlus className="ml-2 h-4 w-4" />
                </Button>
              </Link>
            </div>

            <p className="text-gray-400 text-xs text-center mt-6">Secure access to college attendance management</p>
          </div>
        </div>
      </div>
    </>
  )
}
