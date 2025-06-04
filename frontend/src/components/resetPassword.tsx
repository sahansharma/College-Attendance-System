import { useState } from "react";
import { EyeIcon, EyeOffIcon } from "lucide-react";
import axios from "axios";
import { useSearchParams, useNavigate } from "react-router-dom";
import { toast } from "react-toastify";

const URL = "https://localhost:8000/" + "/api/resetPassword";

const ResetPassword = () => {
  const [searchParams] = useSearchParams();
  let navigate = useNavigate();
  const id = searchParams.get("id");
  const token = searchParams.get("token");

  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  const handleResetPassword = async (ev) => {
    ev.preventDefault(); // Prevent default form submission behavior

    const newpassword = ev.target.newpassword.value;
    const confirmpassword = ev.target.confirmpassword.value;

    if (newpassword !== confirmpassword) {
      toast.error("Passwords do not match!");
      return; // Prevent further execution if passwords don't match
    }

    try {
      const formData = { id, token, password: newpassword };

      // API Call
      const res = await axios.post(URL, formData);

      if (res.data.success) {
        toast.success(res.data.message);
        navigate("/login"); // Navigate to login page on success
      } else {
        toast.error(res.data.message); // Show error from API
      }
    } catch (error) {
      toast.error("An error occurred while resetting the password. Please try again.");
      console.error("Error resetting password:", error);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-100 to-indigo-200 dark:from-gray-900 dark:to-gray-800 flex items-center justify-center p-4">
      <div className="w-full max-w-lg p-8 bg-white dark:bg-gray-800 rounded-2xl shadow-xl transition-all duration-300 ease-in-out hover:shadow-2xl">
        <h1 className="text-3xl font-bold text-gray-800 dark:text-white text-center mb-8">Reset Password</h1>
        <form className="space-y-6" onSubmit={handleResetPassword}>
          {/* New Password Field */}
          <div className="space-y-2">
            <label htmlFor="newpassword" className="text-sm font-medium text-gray-700 dark:text-gray-300">
              New Password
            </label>
            <div className="relative">
              <input
                id="newpassword"
                name="newpassword"
                type={showPassword ? "text" : "password"}
                placeholder="Enter your new password"
                required
                className="w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 focus:ring-2 focus:ring-purple-500 focus:border-transparent dark:bg-gray-700 dark:text-white transition-all duration-300 ease-in-out"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute inset-y-0 right-0 flex items-center pr-3 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors duration-200"
              >
                {showPassword ? <EyeOffIcon className="h-5 w-5" /> : <EyeIcon className="h-5 w-5" />}
              </button>
            </div>
          </div>

          {/* Confirm Password Field */}
          <div className="space-y-2">
            <label htmlFor="confirmpassword" className="text-sm font-medium text-gray-700 dark:text-gray-300">
              Confirm Password
            </label>
            <div className="relative">
              <input
                id="confirmpassword"
                name="confirmpassword"
                type={showConfirmPassword ? "text" : "password"}
                placeholder="Confirm your new password"
                required
                className="w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 focus:ring-2 focus:ring-purple-500 focus:border-transparent dark:bg-gray-700 dark:text-white transition-all duration-300 ease-in-out"
              />
              <button
                type="button"
                onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                className="absolute inset-y-0 right-0 flex items-center pr-3 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors duration-200"
              >
                {showConfirmPassword ? <EyeOffIcon className="h-5 w-5" /> : <EyeIcon className="h-5 w-5" />}
              </button>
            </div>
          </div>

          {/* Submit Button */}
          <div>
            <button
              type="submit"
              className="w-full px-6 py-3 text-white bg-purple-600 rounded-lg hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2 dark:focus:ring-offset-gray-800 transition-all duration-300 ease-in-out transform hover:scale-105"
            >
              Reset Password
            </button>
          </div>

          {/* Footer */}
          <p className="text-center text-sm text-gray-500 dark:text-gray-400">
            Not yet registered?{" "}
            <a
              href="register"
              className="font-semibold text-purple-600 hover:text-purple-500 dark:text-purple-400 dark:hover:text-purple-300 transition-colors duration-200"
            >
              Register Here
            </a>
          </p>
        </form>
      </div>
    </div>
  );
};

export default ResetPassword;
