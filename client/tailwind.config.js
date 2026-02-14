/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Dark CAD-like theme
        cad: {
          dark: '#0a0e1a',      // Main background
          darker: '#060810',     // Darker areas
          panel: '#151b2d',      // Panel background
          border: '#1e2942',     // Borders
          accent: '#2563eb',     // Blue accent (electrical blue)
          success: '#10b981',    // Green for PASS
          warning: '#f59e0b',    // Orange for WARNING
          danger: '#ef4444',     // Red for FAIL
          text: {
            primary: '#e5e7eb',  // Primary text
            secondary: '#9ca3af', // Secondary text
            muted: '#6b7280'     // Muted text
          }
        }
      },
      fontFamily: {
        mono: ['JetBrains Mono', 'Consolas', 'Monaco', 'monospace'],
        sans: ['Inter', 'system-ui', 'sans-serif']
      }
    },
  },
  plugins: [],
}
