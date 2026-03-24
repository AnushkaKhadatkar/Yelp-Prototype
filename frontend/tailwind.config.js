export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        red: { DEFAULT: '#E8321A', dark: '#C4250F', light: '#FFF0ED' },
        cream: '#FDF8F3',
        ink: { DEFAULT: '#1A1208', soft: '#3D3426', muted: '#8C7E6E' },
        gold: { DEFAULT: '#C9942A', light: '#F5E4B8' },
      },
      fontFamily: {
        display: ['"Fraunces"', 'Georgia', 'serif'],
        body: ['"Outfit"', 'sans-serif'],
      },
      borderRadius: { xl: '16px', '2xl': '24px', '3xl': '32px' },
      boxShadow: {
        card: '0 4px 24px rgba(26,18,8,0.07)',
        'card-hover': '0 20px 60px rgba(26,18,8,0.12)',
        red: '0 8px 24px rgba(232,50,26,0.35)',
      },
    },
  },
  plugins: [],
}
