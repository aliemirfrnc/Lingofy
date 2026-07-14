export const colors = {
  theme: "rgb(var(--theme-r) var(--theme-g) var(--theme-b))",
  background: "#0a0a0a",
  surface: "rgba(25, 25, 30, 0.65)",
  surfaceHover: "rgba(255, 255, 255, 0.1)",
  border: "rgba(255, 255, 255, 0.08)",
  text: {
    primary: "#ffffff",
    secondary: "rgba(255, 255, 255, 0.65)",
    muted: "rgba(255, 255, 255, 0.45)",
  }
};

export const shadows = {
  glass: "0 8px 32px 0 rgba(0, 0, 0, 0.37)",
  glow: "0 0 20px 0 rgba(var(--theme-r), var(--theme-g), var(--theme-b), 0.5)",
  card: "0 4px 14px 0 rgba(0,0,0,0.25)"
};

export const radius = {
  sm: "0.375rem",
  md: "0.5rem",
  lg: "0.75rem",
  xl: "1rem",
  "2xl": "1.5rem",
  full: "9999px",
};

export const spacing = {
  xs: "0.25rem",
  sm: "0.5rem",
  md: "1rem",
  lg: "1.5rem",
  xl: "2rem",
};

export const animations = {
  transition: "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
  transitionFast: "all 0.15s cubic-bezier(0.4, 0, 0.2, 1)",
  transitionSlow: "all 0.5s cubic-bezier(0.4, 0, 0.2, 1)",
  easing: "cubic-bezier(0.4, 0, 0.2, 1)",
  bounce: "cubic-bezier(0.34, 1.56, 0.64, 1)"
};

export const typography = {
  fontFamily: "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"
};
