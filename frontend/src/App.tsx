import React from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { useState, useEffect } from "react";
import { ToastContainer } from "react-toastify";
import { Toaster } from "./components/ui/toaster";
import "react-toastify/dist/ReactToastify.css";
import LandingPage from "./components/LandingPage";
import RegistrationForm from "@/components/registration-form"
import LoginForm from "./components/login-form";
import NoPage from "./components/nopage";
import ForgotPassword from "./components/forgotPassword";
import ResetPassword from "./components/resetPassword";
import AdminLoginForm from "./components/admin/admin-login";
import StudentDashboard from './app/dashboard/studentDashboard.tsx';
import Page from './admindash/page.tsx';
import RootLayout from './admindash/layout.tsx';
import StudentsPage from './admindash/students/page.tsx';
import ClassesPage from './admindash/classes/page.tsx';
import AttendancePage from './admindash/attendance/page.tsx';
import ReportsPage from './admindash/reports/page.tsx';

import "./App.css";
import axios from "axios";

export default function Home() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [isLoggedInAdmin, setIsLoggedInAdmin] = useState(false);
  const [email, setEmail] = useState("");
  const [id, setId] = useState(0);

  // Sync authentication state with localStorage
  useEffect(() => {
    const storedIsLoggedIn = JSON.parse(localStorage.getItem("isLoggedIn") || "false");
    const storedEmail = localStorage.getItem("email") || "";
    const storedId = localStorage.getItem("id") || 0;

    setIsLoggedIn(storedIsLoggedIn);
    setEmail(storedEmail);
    setId(storedId);
  }, []);

  useEffect(() => {
    localStorage.setItem("isLoggedIn", JSON.stringify(isLoggedIn));
    localStorage.setItem("email", email);
  }, [isLoggedIn, email]);

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const response = await axios.get('http://127.0.0.1:8000/api/user', { withCredentials: true });
        console.log("response from checkAuth", response.data)  
        if (response.status === 200) {
          setIsLoggedIn(true);
          setId(response.data.id);
          setEmail(response.data.username);
        }
      } catch (error) {
        console.error("Error checking auth:", error);
      }
    };
    checkAuth();
  }, []);

  // Wrapper for protecting routes
  const PrivateRoute = ({ children, isLoggedIn }) => {
    // return isLoggedIn ? children : <Navigate to="/" replace />;
    if (!isLoggedIn) {
      return <Navigate to="/dashboard" />;
    }
    console.log("children", children) 
    console.log("id", id)
    console.log("isLoggedIn", isLoggedIn)
    console.log("email", email)
    return children;
  };

  return (
    <>
      <ToastContainer />
      <Toaster />
      <BrowserRouter>
        <Routes>
          {/* Public Routes */}
          <Route path="/" element={<LandingPage/>} />
          <Route
            path="/login"
            element={
              <LoginForm
                isLoggedIn={isLoggedIn}
                setIsLoggedIn={setIsLoggedIn}
                setEmail={setEmail}
                setId={setId}
              />             
            }
          />
          <Route
            path="/login/admin"
            element={
              <AdminLoginForm
                isLoggedInAdmin={isLoggedInAdmin}
                setIsLoggedInAdmin={setIsLoggedInAdmin}
                setEmail={setEmail}
              />             
            }
          />
          <Route
            path="/register"
            element={
              <RegistrationForm
                // setIsLoggedIn={setIsLoggedIn}
                // setName={setName}
                // setEmail={setEmail}
              />
            }
          />
          <Route
            path="/forgotPassword"
            element={<ForgotPassword />}
          />
          <Route
            path="/resetPassword"
            element={<ResetPassword />}
          />

          {/* Protected Routes */}
          <Route
            path="/dashboard"
            element={
              <PrivateRoute isLoggedIn={isLoggedIn}>
                <StudentDashboard isLoggedIn={isLoggedIn} id={id}/>
              </PrivateRoute>
            }
          />
        
          {/* Fallback Route */}
          <Route path="*" element={<NoPage />} />

          <Route path="/admin-dashboard" element={
          <React.Fragment>
            <RootLayout >
            <Page />
            </RootLayout>
          </React.Fragment>
        } />
        <Route path="/admin-dashboard/students" element={
          <React.Fragment>
            <RootLayout >
            <StudentsPage />
            </RootLayout>
          </React.Fragment>
        } />
        <Route path="/admin-dashboard/classes" element={
          <React.Fragment>
            <RootLayout >
            <ClassesPage />
            </RootLayout>
          </React.Fragment>
        } />
        <Route path="/admin-dashboard/attendance" element={
          <React.Fragment>
            <RootLayout >
            <AttendancePage />
            </RootLayout>
          </React.Fragment>
        } />
        <Route path="/admin-dashboard/reports" element={
          <React.Fragment>
            <RootLayout >
            <ReportsPage />
            </RootLayout>
          </React.Fragment>
        } /> 
        </Routes>
      </BrowserRouter>
    </>
  );
}