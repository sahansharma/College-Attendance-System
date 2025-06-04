import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import './index.css';
import React from 'react';
import App from './App.tsx';
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import DashboardPage from './admindash/layout.tsx';
import { Sidebar } from './components/sidebar.tsx';
import Page from './admindash/page.tsx';
import RootLayout from './admindash/layout.tsx';
import StudentsPage from './admindash/students/page.tsx';
import ClassesPage from './admindash/classes/page.tsx';
import AttendancePage from './admindash/attendance/page.tsx';
import ReportsPage from './admindash/reports/page.tsx';
import { Toaster } from './components/ui/toaster.tsx';

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App /> 
    {/* <Toaster />
      <BrowserRouter>
       <Routes>
        
        <Route path="/" element={
          <React.Fragment>
            <RootLayout >
            <Page />
            </RootLayout>
          </React.Fragment>
        } />
        <Route path="/students" element={
          <React.Fragment>
            <RootLayout >
            <StudentsPage />
            </RootLayout>
          </React.Fragment>
        } />
        <Route path="/classes" element={
          <React.Fragment>
            <RootLayout >
            <ClassesPage />
            </RootLayout>
          </React.Fragment>
        } />
        <Route path="/attendance" element={
          <React.Fragment>
            <RootLayout >
            <AttendancePage />
            </RootLayout>
          </React.Fragment>
        } />
        <Route path="/reports" element={
          <React.Fragment>
            <RootLayout >
            <ReportsPage />
            </RootLayout>
          </React.Fragment>
        } /> 

      </Routes>
    </BrowserRouter> */}
  </StrictMode>
);