import { ArrowRight, Circle } from 'lucide-react'
import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'

export default function Home() {
  const [mounted, setMounted] = useState(false)
  const navigate = useNavigate()

  useEffect(() => {
    setMounted(true)
  }, [])

  return (
    <div className="fixed inset-0 flex items-center justify-center overflow-hidden bg-[#E8E5A8]">
      {/* Top Left Company Logo */}
      <div className={`absolute top-12 left-12 flex items-center gap-3 transition-all duration-700 ${mounted ? 'opacity-100 translate-x-0' : 'opacity-0 -translate-x-10'}`}>
        <Circle className="w-8 h-8 text-[#6B9563] fill-[#6B9563] animate-pulse-glow" />
        <span className="text-lg font-semibold text-[#1a1a1a]">Acsia Technology</span>
      </div>

      {/* Main Content Container */}
      <div className="relative w-full max-w-7xl mx-auto px-16 flex items-center justify-between">
        {/* Left Side - Title */}
        <div className={`max-w-2xl transition-all duration-1000 ${mounted ? 'translate-x-0 opacity-100' : '-translate-x-20 opacity-0'}`}>
          <h1 className="text-7xl font-bold text-[#1a1a1a] leading-tight mb-6 transition-all duration-300 hover:text-[#6B9563] cursor-default">
            INTELLI LEARN AI
          </h1>
          <p className="text-xl text-[#4a4a4a] mb-8 leading-relaxed max-w-xl">
            AI-powered learning platform for personalized skill development and course recommendations.
          </p>
          <button 
            onClick={() => {
              const role = localStorage.getItem('role') || 'guest'
              if (role === 'admin') return navigate('/employees')
              if (role === 'employee') return navigate('/my-analytics')
              return navigate('/login')
            }}
            className="group flex items-center gap-3 px-8 py-4 bg-[#6B9563] text-white font-bold text-lg rounded-lg hover:bg-[#5a7e52] transition-all duration-300 hover:scale-105 hover:-translate-y-1 shadow-lg hover:shadow-[0_12px_35px_rgba(107,149,99,0.5)] relative overflow-hidden"
          >
            <span className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-700"></span>
            <span className="relative">Get Started</span>
            <ArrowRight className="w-6 h-6 transition-transform duration-300 group-hover:translate-x-1 relative" />
          </button>
        </div>

        {/* Right Side - Illustration */}
        <div className={`relative transition-all duration-1000 delay-300 ${mounted ? 'translate-x-0 opacity-100' : 'translate-x-20 opacity-0'}`}>
          {/* Geometric Elements with animations */}
          <div className="absolute top-10 left-10 w-4 h-4 bg-[#6B9563] rounded-full animate-pulse-glow"></div>
          <div className="absolute top-32 right-20 w-20 h-20 border-2 border-[#1a1a1a] rotate-12 transition-transform duration-500 hover:rotate-45 hover:scale-110"></div>
          <div className="absolute bottom-20 left-0 w-16 h-16 border-2 border-[#6B9563] rounded-lg transition-transform duration-700 hover:rotate-180"></div>
          <div className="absolute top-1/2 right-0 w-24 h-24 border-2 border-[#D4C5F9] rounded-lg rotate-45 opacity-50 animate-float"></div>
          
          {/* Person Illustration (SVG) */}
          <svg width="450" height="500" viewBox="0 0 450 500" fill="none" xmlns="http://www.w3.org/2000/svg" className="relative z-10">
            {/* Background circles */}
            <circle cx="225" cy="200" r="120" fill="#F5E8D8" opacity="0.6"/>
            <circle cx="240" cy="180" r="30" fill="#D4C5F9" opacity="0.8"/>
            
            {/* Head */}
            <ellipse cx="225" cy="140" rx="50" ry="55" fill="#FFB8B8"/>
            
            {/* Hair */}
            <path d="M 180 120 Q 225 90 270 120 Q 270 135 245 140 Q 225 145 205 140 Q 180 135 180 120" fill="#4a4a4a"/>
            
            {/* Eyes */}
            <circle cx="210" cy="140" r="3" fill="#1a1a1a"/>
            <circle cx="240" cy="140" r="3" fill="#1a1a1a"/>
            
            {/* Smile */}
            <path d="M 200 160 Q 225 170 250 160" stroke="#1a1a1a" strokeWidth="2" strokeLinecap="round" fill="none"/>
            
            {/* Torso */}
            <ellipse cx="225" cy="280" rx="90" ry="110" fill="#6B9563"/>
            
            {/* Arm (left - reaching up) */}
            <ellipse cx="170" cy="250" rx="30" ry="85" fill="#6B9563" transform="rotate(-35 170 250)"/>
            <ellipse cx="150" cy="190" rx="22" ry="28" fill="#FFB8B8"/>
            
            {/* Arm (right - reaching to side) */}
            <ellipse cx="280" cy="280" rx="30" ry="75" fill="#6B9563" transform="rotate(25 280 280)"/>
            <ellipse cx="310" cy="320" rx="22" ry="28" fill="#FFB8B8"/>
            
            {/* Lower Body/Sitting position */}
            <path d="M 160 360 Q 150 420 140 470 L 170 480 Q 180 450 190 420 L 225 390 L 260 420 Q 270 450 280 480 L 310 470 Q 300 420 290 360 Z" fill="#8BC34A"/>
            
            {/* Neck */}
            <rect x="210" y="185" width="30" height="35" fill="#FFB8B8"/>
            
            {/* Floating square */}
            <rect x="320" y="160" width="60" height="60" fill="#F5E8D8" stroke="#4a4a4a" strokeWidth="2" rx="5"/>
            
            {/* Wavy line decoration */}
            <path d="M 320 200 Q 340 190 360 200 Q 380 210 400 200" stroke="#8BC34A" strokeWidth="4" fill="none" strokeLinecap="round"/>
          </svg>

          {/* Additional geometric elements */}
          <div className="absolute top-24 left-32 text-4xl font-bold text-[#1a1a1a] transition-transform duration-300 hover:rotate-90 hover:scale-125 cursor-default">+</div>
          
          {/* Floating particles for extra flair */}
          <div className="absolute -top-10 right-40 w-2 h-2 bg-[#6B9563] rounded-full animate-bounce-subtle" style={{ animationDelay: '0.5s' }}></div>
          <div className="absolute bottom-40 -left-10 w-3 h-3 bg-[#D4C5F9] rounded-full animate-bounce-subtle" style={{ animationDelay: '1s' }}></div>
        </div>
      </div>
    </div>
  )
}
