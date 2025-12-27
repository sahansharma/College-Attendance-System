# College Attendance System

A web-based attendance management system built with React, Django, and Tailwind CSS for academic institutions.

## Overview

This project was created to solve the manual attendance tracking problems we faced in our college. Instead of the traditional paper-based method, I built this system to automate attendance management using facial recognition technology. The system allows students, faculty, and administrators to interact with attendance data in real-time.

## Technologies Used

- React.js (Frontend)
- Django (Backend API)
- SQLite3 (Database)
- Tailwind CSS (Styling)
- JavaScript ES6+

## Getting Started

### Requirements

Make sure you have these installed on your system:
- Node.js (version 16 or newer)
- Python 3.9 or newer
- pip package manager

### Setup Instructions

1. **Clone the project**
   ```bash
   git clone https://github.com/your-username/college-attendance-system.git
   cd college-attendance-system
   ```

2. **Set up the backend**
   ```bash
   cd backend
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py runserver
   ```

3. **Set up the frontend**
   ```bash
   cd frontend
   npm install
   npm start
   ```

The application should be running at http://localhost:3000

## How It Works

### For Students
- Log in to check your attendance records
- Download attendance reports for your records
- View real-time attendance status

### For Faculty
- Mark attendance using the facial recognition feature
- Manage class schedules and attendance reports
- Track student attendance patterns

### For Administrators
- Manage user accounts and permissions
- Generate comprehensive attendance reports
- Monitor overall attendance trends

## Current Features

- User authentication with role-based access
- Facial recognition for attendance marking
- Real-time attendance tracking
- Responsive design for mobile and desktop
- Attendance reports and analytics

## Future Plans

I'm working on adding these features:
- Downloadable attendance reports in PDF format
- Biometric authentication support
- Mobile application
- Email notifications for attendance issues
- Advanced analytics dashboard

## Contributing

If you'd like to contribute to this project:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - feel free to use it for your own projects.

## Contact

If you have questions or suggestions, feel free to reach out:

- GitHub: [your-username](https://github.com/your-username)
- Email: your.email@example.com

## Acknowledgments

Thanks to the Django and React communities for their excellent documentation and resources that made this project possible.
