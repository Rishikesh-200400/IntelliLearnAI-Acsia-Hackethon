import { useEffect, useRef } from 'react'

export function useScrollReveal(threshold = 0) {
  const elementRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const element = elementRef.current
    if (!element) return

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add('revealed')
          }
        })
      },
      {
        threshold,
        rootMargin: '0px 0px -50px 0px'
      }
    )

    observer.observe(element)

    // Fallback: if already visible but observer didn't fire yet, reveal immediately
    const rect = element.getBoundingClientRect()
    if (rect.top < window.innerHeight && rect.bottom > 0) {
      element.classList.add('revealed')
    }

    return () => {
      if (element) observer.unobserve(element)
    }
  }, [threshold])

  return elementRef
}
