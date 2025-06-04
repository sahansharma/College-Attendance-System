import type { Metadata } from "next"
import { Sidebar } from "@/components/sidebar"
import type React from "react"
import { ModeToggle } from "@/components/mode-toggler"
import { UserNav } from "@/components/user-nav"
import { ThemeProvider } from "@/components/theme-provider"
import { Bell, Search } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"

export const metadata: Metadata = {
  title: "tem",
  description: "Manage student attendance efficiently",
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
      <div className="fixed inset-0 flex">
        {/* Sidebar - Hidden on mobile, visible on md+ */}
        <div className="hidden md:block w-64 flex-shrink-0 border-r bg-card">
          <Sidebar />
        </div>

        {/* Main Content Area */}
        <div className="flex-1 flex flex-col min-w-0">
          {/* Header */}
          <header className="sticky top-0 z-40 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 border-b">
            <div className="h-16 flex items-center justify-between px-4 md:px-6 gap-4">
              {/* Mobile Menu Button */}
              <Button variant="outline" size="icon" className="md:hidden">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="24"
                  height="24"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  className="h-5 w-5"
                >
                  <line x1="4" x2="20" y1="12" y2="12" />
                  <line x1="4" x2="20" y1="6" y2="6" />
                  <line x1="4" x2="20" y1="18" y2="18" />
                </svg>
                <span className="sr-only">Toggle menu</span>
              </Button>

              

              {/* Right Side Actions */}
              <div className="flex items-center gap-2">
                <Button variant="ghost" size="icon" className="text-muted-foreground">
                  <Bell className="h-5 w-5" />
                  <span className="sr-only">Notifications</span>
                </Button>
                <ModeToggle />
                <UserNav />
              </div>
            </div>
          </header>

          {/* Main Content - Full width with proper padding */}
          <main className="flex-1 overflow-y-auto bg-muted/40 p-6">
            <div className="max-w-full mx-auto">{children}</div>
          </main>
        </div>
      </div>
    </ThemeProvider>
  )
}