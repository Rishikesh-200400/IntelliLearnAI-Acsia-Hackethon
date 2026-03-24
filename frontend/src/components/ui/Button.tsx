import { cn } from '@/lib/utils'
import { ButtonHTMLAttributes } from 'react'

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline'
  size?: 'sm' | 'md' | 'lg'
}

export function Button({ 
  children, 
  className, 
  variant = 'primary', 
  size = 'md',
  ...props 
}: ButtonProps) {
  const baseStyles = "font-bold rounded-lg transition-all duration-300 inline-flex items-center justify-center relative overflow-hidden group disabled:opacity-50 disabled:cursor-not-allowed"
  
  const variants = {
    primary: "bg-[#6B9563] text-white hover:bg-[#5a7e52] hover:shadow-lg hover:scale-105 hover:-translate-y-0.5",
    secondary: "bg-[#D4D1A0] text-[#1a1a1a] hover:bg-[#C4C190] hover:shadow-lg hover:scale-105",
    outline: "border-2 border-[#6B9563] text-[#6B9563] hover:bg-[#6B9563] hover:text-white hover:shadow-lg hover:scale-105"
  }
  
  const sizes = {
    sm: "px-4 py-2 text-sm",
    md: "px-6 py-3 text-base",
    lg: "px-8 py-4 text-lg"
  }
  
  return (
    <button 
      className={cn(baseStyles, variants[variant], sizes[size], className)}
      {...props}
    >
      {/* Shimmer effect on hover */}
      <span className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-700"></span>
      <span className="relative z-10 flex items-center gap-2">{children}</span>
    </button>
  )
}
