import React from 'react';
import { Navigate } from 'react-router-dom';

interface PrivateRouteProps {
  children: React.ReactNode;
  isLoggedIn?: boolean;
  isLoggedInAdmin?: boolean;
}

const PrivateRoute: React.FC<PrivateRouteProps> = ({ children, isLoggedIn, isLoggedInAdmin }) => {
  if (isLoggedInAdmin !== undefined) {
    return isLoggedInAdmin ? <>{children}</> : <Navigate to="/admin-login" />;
  }
  return isLoggedIn ? <>{children}</> : <Navigate to="/login" />;
};

export default PrivateRoute;