import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import type { Attendance } from "@/lib/types"

function getInitials(firstName: string, lastName: string): string {
  return `${(firstName || "").charAt(0) || ""}${(lastName || "").charAt(0) || ""}`.toUpperCase()
}

export function RecentAttendance({ data }: { data: Attendance[] }) {
  return (
    <div className="space-y-8">
      {data.map((entry) => (
        console.log(entry),
        <div key={entry.id} className="flex items-center">
          <Avatar className="h-9 w-9">
            {/* <AvatarImage src={entry.student.student_img} alt={entry.student.first_name} /> */}
            <AvatarFallback>{getInitials(entry.first_name, entry.last_name)}</AvatarFallback>
          </Avatar>
          <div className="ml-4 space-y-1">
            <p className="text-sm font-medium leading-none">{entry.first_name} {entry.last_name}</p>
            <p className="text-sm text-muted-foreground">{entry.username}</p>
          </div>
          <div className="ml-auto font-medium">
            {entry.status === "Present" && <span className="text-green-500">Present</span>}
            {entry.status === "Absent" && <span className="text-red-500">Absent</span>}
            {entry.status === "Late" && <span className="text-yellow-500">Late</span>}
          </div>
        </div>
      ))}
    </div>
  )
}