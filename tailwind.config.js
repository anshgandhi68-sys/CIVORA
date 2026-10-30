/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        ink: '#01030F',
        brand: {
          blue: '#0071FF',
          hover: '#8FC2FF',
          focus: '#4DA3FF',
          surface: 'rgba(4,9,23,0.97)',
          border: 'rgba(255,255,255,0.18)',
        }
      },
      fontFamily: {
        display: ['Instrument Serif', 'Georgia', 'serif'],
        sans: ['Manrope', '-apple-system', 'BlinkMacSystemFont', 'sans-serif'],
        mono: ['IBM Plex Mono', 'monospace'],
      }
    },
  },
  plugins: [],
}

