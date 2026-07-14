import * as React from "react"
import { cn } from "../../lib/utils"

const Button = React.forwardRef(({ className, variant = "primary", size = "default", ...props }, ref) => {
  const baseStyles = "inline-flex items-center justify-center whitespace-nowrap rounded-xl text-sm font-semibold transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-theme disabled:pointer-events-none disabled:opacity-50"
  
  const variants = {
    primary: "bg-theme hover:bg-theme-600 text-white shadow-glow border border-white/10 hover:-translate-y-0.5",
    secondary: "bg-white/5 hover:bg-white/10 border border-white/10 text-white backdrop-blur-sm",
    ghost: "hover:bg-white/10 text-white/70 hover:text-white",
    danger: "bg-red-500/10 text-red-500 hover:bg-red-500/20 border border-red-500/20",
    premium: "bg-gradient-to-r from-purple-500 to-indigo-500 hover:from-purple-400 hover:to-indigo-400 text-white shadow-[0_0_20px_rgba(168,85,247,0.4)] border border-white/20 hover:-translate-y-0.5",
  }
  
  const sizes = {
    default: "h-11 px-5 py-2",
    sm: "h-9 rounded-lg px-3 text-xs",
    lg: "h-14 rounded-2xl px-8 text-base",
    icon: "h-11 w-11",
  }

  return (
    <button
      className={cn(baseStyles, variants[variant], sizes[size], className)}
      ref={ref}
      {...props}
    />
  )
})
Button.displayName = "Button"

export { Button }
