import { useState, MouseEvent } from 'react'

interface Ripple {
  x: number
  y: number
  size: number
  id: number
}

export function useRipple() {
  const [ripples, setRipples] = useState<Ripple[]>([])

  const addRipple = (event: MouseEvent<HTMLElement>) => {
    const element = event.currentTarget
    const rect = element.getBoundingClientRect()
    
    // Calculate ripple position relative to element
    const x = event.clientX - rect.left
    const y = event.clientY - rect.top
    
    // Calculate ripple size to cover entire element
    const size = Math.max(rect.width, rect.height) * 2
    
    const newRipple: Ripple = {
      x,
      y,
      size,
      id: Date.now() + Math.random() // More unique ID
    }
    
    setRipples(prev => [...prev, newRipple])
    
    // Remove ripple after animation completes
    setTimeout(() => {
      setRipples(prev => prev.filter(ripple => ripple.id !== newRipple.id))
    }, 600)
  }

  return { ripples, addRipple }
}
