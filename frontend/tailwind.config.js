/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      borderRadius: {
        'custom': '12px',  // Custom value example
        'large': '24px',   // Another custom value example
      }
    }
  },
  plugins: [],
}

