import axios from 'axios';

interface RegistrationData {
  username: string;
  password: string;
  first_name: string;
  middle_name?: string;
  last_name: string;
  student_class: {
    name: string;
    section: string;
    semester: string;
    year: number;
  };
  student_img?: string; // Assuming student_img is a base64 encoded string
}

interface ApiResponse {
  success: boolean;
  message: string;
  data?: any;
}

// Create axios instance with base URL
const api = axios.create({
  baseURL: "http://localhost:8000/api",
  headers: {
    "Content-Type": "application/json",
  },
})

// Registration service
export const registerStudent = async (data: RegistrationData): Promise<ApiResponse> => {
  try {
    console.log("Data", data);

    const response = await api.post("/register", data);
    return {
      success: true,
      message: "Registration successful",
      data: response.data,
    }
  } catch (error) {
    if (axios.isAxiosError(error)) {
      return {
        success: false,
        message: error.response?.data?.message || "Registration failed. Please try again.",
      }
    }
    return {
      success: false,
      message: "An unexpected error occurred",
    }
  }
}

