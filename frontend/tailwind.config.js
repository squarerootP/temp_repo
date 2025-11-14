/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        roboto: ['Roboto', 'sans-serif'],
        poppins: ['Poppins', 'sans-serif'],
      },
      gridTemplateColumns: {
        '70/30': '70% 30%',
      },
      colors: {
        primary: '#16a34a', // Tailwind green-600
        mid: '#22c55e', // Tailwind green-500
        secondary: '#bbf7d0', // Tailwind green-200
        'heavy-primary': '#166534', // Tailwind green-800
      },
    },
  },
  plugins: [],
};
