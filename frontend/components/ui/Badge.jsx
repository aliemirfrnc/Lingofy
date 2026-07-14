import * as React from "react"
import { cn } from "../../lib/utils"

function Badge({ className, variant = "default", ...props }) {
  const baseStyles = "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-theme focus:ring-offset-2"
  
  const variants = {
    default: "border-transparent bg-theme-100 text-theme",
    secondary: "border-transparent bg-white/10 text-white/80",
    outline: "text-white/80 border-white/20",
    premium: "border-transparent bg-purple-500/20 text-purple-400 border border-purple-500/30",
    warning: "border-transparent bg-yellow-500/20 text-yellow-500 border border-yellow-500/30",
  }

  return (
    <div className={cn(baseStyles, variants[variant], className)} {...props} />
  )
}

export { Badge }
