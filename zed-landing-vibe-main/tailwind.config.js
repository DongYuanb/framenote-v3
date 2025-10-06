/** @type {import('tailwindcss').Config} */
export default {
  darkMode: ["class"],
  content: [
    './pages/**/*.{ts,tsx}',
    './components/**/*.{ts,tsx}',
    './app/**/*.{ts,tsx}',
    './src/**/*.{ts,tsx}',
    './index.html',
  ],
  prefix: "",
  theme: {
    container: {
      center: true,
      padding: "2rem",
      screens: {
        "2xl": "1400px",
      },
    },
    extend: {
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
        sidebar: {
          DEFAULT: "hsl(var(--sidebar-background))",
          foreground: "hsl(var(--sidebar-foreground))",
          primary: "hsl(var(--sidebar-primary))",
          "primary-foreground": "hsl(var(--sidebar-primary-foreground))",
          accent: "hsl(var(--sidebar-accent))",
          "accent-foreground": "hsl(var(--sidebar-accent-foreground))",
          border: "hsl(var(--sidebar-border))",
          ring: "hsl(var(--sidebar-ring))",
        },
      },
      fontFamily: {
        sans: ["-apple-system", "BlinkMacSystemFont", "SF Pro Display", "SF Pro Text", "Helvetica Neue", "Helvetica", "Arial", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "WenQuanYi Micro Hei", "sans-serif"],
        display: ["SF Pro Display", "-apple-system", "BlinkMacSystemFont", "serif"],
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      keyframes: {
        "accordion-down": {
          from: { height: "0" },
          to: { height: "var(--radix-accordion-content-height)" },
        },
        "accordion-up": {
          from: { height: "var(--radix-accordion-content-height)" },
          to: { height: "0" },
        },
        // Added subtle motion primitives
        "fade-in": {
          "0%": { opacity: "0", transform: "translateY(10px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        "fade-out": {
          "0%": { opacity: "1", transform: "translateY(0)" },
          "100%": { opacity: "0", transform: "translateY(10px)" },
        },
        "scale-in": {
          "0%": { transform: "scale(0.98)", opacity: "0" },
          "100%": { transform: "scale(1)", opacity: "1" },
        },
        "scale-out": {
          from: { transform: "scale(1)", opacity: "1" },
          to: { transform: "scale(0.98)", opacity: "0" },
        },
        "slide-in-right": {
          "0%": { transform: "translateX(100%)" },
          "100%": { transform: "translateX(0)" },
        },
        "slide-out-right": {
          "0%": { transform: "translateX(0)" },
          "100%": { transform: "translateX(100%)" },
        },
      },
      animation: {
        "accordion-down": "accordion-down 0.2s ease-out",
        "accordion-up": "accordion-up 0.2s ease-out",
        "fade-in": "fade-in 0.3s ease-out",
        "fade-out": "fade-out 0.3s ease-out",
        "scale-in": "scale-in 0.2s ease-out",
        "scale-out": "scale-out 0.2s ease-out",
        "slide-in-right": "slide-in-right 0.3s ease-out",
        "slide-out-right": "slide-out-right 0.3s ease-out",
        enter: "fade-in 0.3s ease-out, scale-in 0.2s ease-out",
        exit: "fade-out 0.3s ease-out, scale-out 0.2s ease-out",
      },
    },
  },
  plugins: [
    require("tailwindcss-animate"),
    function({ addUtilities }) {
      addUtilities({
        '.grid-pattern': {
          'background-image': `
            linear-gradient(to right, hsl(var(--grid-lines)) 1px, transparent 1px),
            linear-gradient(to bottom, hsl(var(--grid-lines)) 1px, transparent 1px)
          `,
          'background-size': '32px 32px, 32px 32px',
          'background-position': 'center',
          'mask-image': 'radial-gradient(closest-side, #000, rgba(0,0,0,0.6))',
        },
        '.bg-spotlight': {
          'background': 'radial-gradient(600px circle at var(--x, 50%) var(--y, 50%), hsl(var(--primary) / 0.12), transparent 60%)',
          'transition': 'background 150ms ease-out',
        },
        '.edge-ornaments': {
          'position': 'relative',
        },
        '.edge-ornaments::before': {
          'content': '""',
          'position': 'absolute',
          'top': '48px',
          'bottom': '48px',
          'left': '16px',
          'width': '1px',
          'background': 'hsl(var(--grid-lines))',
          'opacity': '0.6',
          'pointer-events': 'none',
        },
        '.edge-ornaments::after': {
          'content': '""',
          'position': 'absolute',
          'top': '48px',
          'bottom': '48px',
          'right': '16px',
          'width': '1px',
          'background': 'hsl(var(--grid-lines))',
          'opacity': '0.6',
          'pointer-events': 'none',
        },
        '.paper-noise': {
          'background-color': 'hsl(var(--background))',
          'background-image': `
            radial-gradient(hsl(var(--grid-dots) / 0.35) 0.5px, transparent 0.6px),
            radial-gradient(hsl(var(--grid-dots) / 0.25) 0.5px, transparent 0.6px)
          `,
          'background-size': '2px 2px, 3px 3px',
          'background-position': '0 0, 1px 1px',
        },
        '.grid-stripes': {
          'position': 'relative',
        },
        '.grid-stripes::before': {
          'content': '""',
          'position': 'absolute',
          'left': '0',
          'right': '0',
          'top': '-1px',
          'height': '56px',
          'pointer-events': 'none',
          'background-image': `
            linear-gradient(to right, hsl(var(--grid-lines)) 1px, transparent 1px),
            linear-gradient(to bottom, hsl(var(--grid-lines)) 1px, transparent 1px)
          `,
          'background-size': '32px 32px',
          'opacity': '0.45',
          'mask-image': 'linear-gradient(to bottom, black, transparent)',
        },
        '.grid-stripes::after': {
          'content': '""',
          'position': 'absolute',
          'left': '0',
          'right': '0',
          'bottom': '-1px',
          'height': '56px',
          'pointer-events': 'none',
          'background-image': `
            linear-gradient(to right, hsl(var(--grid-lines)) 1px, transparent 1px),
            linear-gradient(to bottom, hsl(var(--grid-lines)) 1px, transparent 1px)
          `,
          'background-size': '32px 32px',
          'background-position': '16px 16px',
          'opacity': '0.35',
          'mask-image': 'linear-gradient(to top, black, transparent)',
        },
      })
    }
  ],
}