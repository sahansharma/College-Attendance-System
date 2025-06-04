import { NavLink, useLocation, useNavigate } from "react-router-dom"
import {
  Home,
  BookOpen,
  Users,
  Calendar,
  FileText,
  Settings,
  LayoutDashboard,
  LogOut,
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Separator } from "@/components/ui/separator"

const links = [
  { name: "Dashboard", href: "/admin-dashboard", icon: Home },
  { name: "Classes", href: "/admin-dashboard/classes", icon: BookOpen },
  { name: "Students", href: "/admin-dashboard/students", icon: Users },
  { name: "Reports", href: "/admin-dashboard/reports", icon: FileText },
  // Add more if needed
]

export function Sidebar() {
  const location = useLocation()
  const navigate = useNavigate()

  const handleLogout = () => {
    navigate("/login/admin")
  }

  return (
    <div className="flex flex-col h-full p-3 w-full bg-gray-900 text-white">
      <div className="flex items-center gap-2 px-1 py-3">
        <LayoutDashboard className="h-5 w-5" />
        <span className="font-semibold text-sm">Attendance System</span>
      </div>

      <div className="flex flex-col gap-2 flex-1 mt-3">
        {links.map((link) => {
          const LinkIcon = link.icon
          const isActive = location.pathname === link.href
          return (
            <NavLink
              key={link.name}
              to={link.href}
              className={({ isActive }) =>
                `flex items-center gap-2 w-full p-2 rounded-md text-sm font-medium ${
                  isActive
                    ? "bg-gray-800 text-white"
                    : "text-gray-400 hover:bg-gray-700 hover:text-white"
                }`
              }
            >
              <LinkIcon className="h-4 w-4" />
              <span>{link.name}</span>
            </NavLink>
          )
        })}
      </div>

      <Separator className="my-3 bg-gray-700" />

      <div className="flex flex-col gap-2 pb-3">
        <Button
          variant="ghost"
          onClick={handleLogout}
          className="justify-start gap-2 w-full p-2 text-gray-400 hover:text-white hover:bg-gray-700"
        >
          <LogOut className="h-4 w-4" />
          <span>Logout</span>
        </Button>
      </div>
    </div>
  )
}
