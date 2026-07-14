import * as React from "react"
import { cn } from "../../lib/utils"

const Avatar = React.forwardRef(({ className, src, alt, fallback, size = "default", ...props }, ref) => {
  const sizes = {
    sm: "h-8 w-8 text-xs",
    default: "h-10 w-10 text-sm",
    lg: "h-14 w-14 text-base",
    xl: "h-20 w-20 text-xl",
  }

  return (
    <div
      ref={ref}
      className={cn(
        "relative flex shrink-0 overflow-hidden rounded-full bg-surface border border-white/10",
        sizes[size],
        className
      )}
      {...props}
    >
      {src ? (
        // eslint-disable-next-line @next/next/no-img-element
        <img
          src={src}
          alt={alt}
          className="aspect-square h-full w-full object-cover"
        />
      ) : (
        <div className="flex h-full w-full items-center justify-center bg-white/5 text-white/70 font-semibold">
          {fallback}
        </div>
      )}
    </div>
  )
})
Avatar.displayName = "Avatar"

export { Avatar }
