import axios from "axios";
const BASE_URL = "http://127.0.0.1:8000";
// const BASE_URL = "http://127.0.0.1:8000/";


export const fetchData = async () => {
  const response = await fetch(`${BASE_URL}/api/`); 
  const data = await response.json();
  return data;
  // return response.data;
};


//csrf token currently not used
export const getCSRFToken = async () => {
  const response = await axios.get(`${BASE_URL}/api/csrf/`, {
    withCredentials: true, // Needed to handle cookies
  });
  return response.data.csrfToken;
};


export const getStudents = async () => {
  const response = await fetch(`${BASE_URL}/students/`);
  const data = await response.json();
  return data;
};

export const getStudentById = async (student_id) => {
  const response = await fetch(`${BASE_URL}/students/${student_id}/`);
  const data = await response.json();
  return data;
};

export const getClasses = async () => {
  const response = await fetch(`${BASE_URL}/classes/`);
  const data = await response.json();
  return data;
};

export const getClassById = async (class_id) => {
  const response = await fetch(`${BASE_URL}/classes/${class_id}/`);
  const data = await response.json();
  return data;
};

export const getStudentDashboard = async (user_id) => {
  const response = await fetch(`${BASE_URL}/api/student_dashboard/${user_id}/`);
  const data = await response.json();
  return data;
};


export const verifyStudentIdentity = async (user_id, imageFile) => {
  const formData = new FormData();
  formData.append("user_id", user_id);
  formData.append("image", imageFile);

  const response = await fetch(`${BASE_URL}/api/verify_student_identity/`, {
    method: "POST",
    body: formData,
  });

  const data = await response.json();
  return data;
};

export const logout = async () => {
  const response = await fetch(`${BASE_URL}/api/logout`, {
    method: "POST",
    credentials: "include", // Ensures cookies (JWT) are included
  });

  if (!response.ok) {
    const error = await response.json()
    console.error('Error response: ', error);
    throw new Error("Logout failed");
  }

  return response.json();
};
