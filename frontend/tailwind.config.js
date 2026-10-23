/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,js}'],
  theme: {
    extend: {
      fontFamily: { sans: ['"Plus Jakarta Sans"', 'system-ui', 'sans-serif'] },
      // Warna utama sama dengan prototype HTML
      colors: { navy: '#1E3A8A', amber: '#F59E0B', success: '#10B981', danger: '#DC2626' },
      keyframes: { fadeIn: { from: { opacity: 0, transform: 'translateY(8px)' }, to: { opacity: 1, transform: 'none' } } },
      animation: { 'fade-in': 'fadeIn .2s ease-out both' },
    },
  },
  plugins: [],
}
