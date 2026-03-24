import { cn } from '@/lib/utils'

interface CardProps {
  children: React.ReactNode
  className?: string
}

export function Card({ children, className }: CardProps) {
  return (
    <div className={cn(
      "bg-[#F5F2D0]/95 backdrop-blur-sm rounded-2xl shadow-lg border border-[#D4D1A0] p-6 transition-all duration-300 hover:shadow-[0_12px_40px_rgba(107,149,99,0.15)] hover:-translate-y-1 hover:border-[#6B9563]/30 animate-scale-in",
      className
    )}>
      {children}
    </div>
  )
}

export function CardHeader({ children, className }: CardProps) {
  return (
    <div className={cn("mb-4", className)}>
      {children}
    </div>
  )
}

export function CardTitle({ children, className }: CardProps) {
  return (
    <h3 className={cn("text-2xl font-bold text-[#1a1a1a]", className)}>
      {children}
    </h3>
  )
}

export function CardDescription({ children, className }: CardProps) {
  return (
    <p className={cn("text-[#4a4a4a] mt-2", className)}>
      {children}
    </p>
  )
}

export function CardContent({ children, className }: CardProps) {
  return (
    <div className={cn("", className)}>
      {children}
    </div>
  )
}
