/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'aspen-blue': '#1e40af',
        'aspen-light-blue': '#3b82f6',
        'aspen-green': '#10b981',
        'aspen-gray': '#6b7280'
      },
      fontFamily: {
        'sans': ['Inter', 'ui-sans-serif', 'system-ui']
      }
    },
  },
  plugins: [],
}