import { Card, CardContent } from "./card"

export default function FeatureCard({ icon, title, description }: { 
  icon: React.ReactNode
  title: string
  description: string 
}) {
  return (
    <Card>
      <CardContent className="flex flex-col items-center space-y-4 p-6">
        <div className="text-primary">
          {icon}
        </div>
        <h3 className="text-xl font-bold">{title}</h3>
        <p className="text-muted-foreground text-center">{description}</p>
      </CardContent>
    </Card>
  )
}