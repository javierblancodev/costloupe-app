import { Link } from "@tanstack/react-router"

import { useTheme } from "@/components/theme-provider"
import { cn } from "@/lib/utils"
import icon from "/assets/images/fastapi-icon.svg"
import iconLight from "/assets/images/fastapi-icon-light.svg"

interface LogoProps {
  variant?: "full" | "icon" | "responsive"
  className?: string
  asLink?: boolean
}

export function Logo({
  variant = "full",
  className,
  asLink = true,
}: LogoProps) {
  const { resolvedTheme } = useTheme()
  const isDark = resolvedTheme === "dark"

  const iconLogo = isDark ? iconLight : icon

  const content =
    variant === "responsive" ? (
      <div className="flex items-center gap-2">
        <img
          src={iconLogo}
          alt="Costloupe"
          className={cn("size-6", className)}
        />
        <span className="text-lg font-semibold group-data-[collapsible=icon]:hidden">
          Costloupe
        </span>
      </div>
    ) : variant === "icon" ? (
      <img src={iconLogo} alt="Costloupe" className={cn("size-5", className)} />
    ) : (
      <div className={cn("flex items-center gap-3", className)}>
        <img src={iconLogo} alt="Costloupe" className="h-full w-auto" />
        <span className="text-4xl font-bold">Costloupe</span>
      </div>
    )

  if (!asLink) {
    return content
  }

  return <Link to="/">{content}</Link>
}
