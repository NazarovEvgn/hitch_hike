/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Brand colors
        'primary': '#27126A',     // Purple
        'accent': '#98EA14',      // Green
        'primary-dark': '#1A0D47',
        'primary-light': '#3D1D9C',
      },
    },
  },
  plugins: [],
}
