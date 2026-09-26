/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        base: {
          DEFAULT: '#070B12',
          50: '#0B111A',
          100: '#101823',
        },
        panel: {
          DEFAULT: '#111923',
          light: '#151F2B',
        },
        border: {
          DEFAULT: '#1E2A38',
          light: '#253242',
        },
        accent: {
          DEFAULT: '#3B82F6',
          muted: '#2563EB',
          dim: 'rgba(59, 130, 246, 0.15)',
        },
        semantic: {
          success: '#22C55E',
          warning: '#EAB308',
          critical: '#EF4444',
          info: '#3B82F6',
        },
        text: {
          primary: '#F1F5F9',
          secondary: '#94A3B8',
          tertiary: '#64748B',
          muted: '#475569',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      fontSize: {
        'telemetry': ['1.125rem', { lineHeight: '1', fontWeight: '500' }],
        'label': ['0.6875rem', { lineHeight: '1.2', letterSpacing: '0.02em' }],
        'meta': ['0.625rem', { lineHeight: '1.2' }],
      },
    },
  },
  plugins: [],
}
