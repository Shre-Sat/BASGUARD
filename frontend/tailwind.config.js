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
          DEFAULT: '#05080E',
          50: '#0A0E17',
          100: '#0F172A',
          200: '#1E293B',
        },
        panel: {
          DEFAULT: '#0D1320',
          light: '#131B2E',
          border: 'rgba(255, 255, 255, 0.08)',
        },
        isro: {
          orange: '#FF9933',
          green: '#138808',
          blue: '#000080',
          cyan: '#06B6D4',
        },
        accent: {
          DEFAULT: '#3B82F6',
          glow: '#60A5FA',
          muted: '#2563EB',
          dim: 'rgba(59, 130, 246, 0.12)',
        },
        semantic: {
          success: '#10B981',
          warning: '#F59E0B',
          critical: '#EF4444',
          info: '#3B82F6',
        },
        text: {
          primary: '#F8FAFC',
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
        'telemetry': ['1.125rem', { lineHeight: '1', fontWeight: '600' }],
        'label': ['0.6875rem', { lineHeight: '1.2', letterSpacing: '0.04em' }],
        'meta': ['0.625rem', { lineHeight: '1.2' }],
      },
      boxShadow: {
        'glow-accent': '0 0 20px rgba(59, 130, 246, 0.25)',
        'glow-isro': '0 0 20px rgba(255, 153, 51, 0.25)',
        'glow-critical': '0 0 20px rgba(239, 68, 68, 0.3)',
        'glow-success': '0 0 20px rgba(16, 185, 129, 0.25)',
      },
      animation: {
        'spin-slow': 'spin 12s linear infinite',
        'pulse-fast': 'pulse 1s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      }
    },
  },
  plugins: [],
}
