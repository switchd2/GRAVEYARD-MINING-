/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        background: '#090D16',
        surface: '#111827',
        surfaceBorder: '#1F293D',
        accentGlow: '#6366F1',
        danger: '#EF4444',
        warning: '#F59E0B',
        success: '#10B981',
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'glow-card': 'radial-gradient(circle at top left, rgba(99, 102, 241, 0.15), transparent 60%)',
      },
    },
  },
  plugins: [],
}
