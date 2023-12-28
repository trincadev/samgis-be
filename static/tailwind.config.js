/** @type {import('tailwindcss').Config} */
import defaultTheme from 'tailwindcss/defaultTheme'

export default {
  content: [
    "./dist/index.html",
    "./src/**/*.{vue,js,ts}",
  ],
  theme: {
    extend: {
      screens: {
        'xxs': '300px',
        'xs': '512px',
        'sm': '768px',
        'md': '896px',
        'tall': {
          'raw': `only screen and ((max-height: 960px) and (max-width: 480px)) or (max-width: 512px)`
        },
        'verySmallTablet': {
          'raw': `only screen and (max-height: 800px) and (max-width: 600px)`
        },
        'notVerySmallTablet': {
          'raw': `only screen and (min-height: 800px) and (min-width: 600px)`
        },
        'smallTablet': {
          'raw': 'only screen and (max-height: 1030px) and (max-width: 770px)'
        },
        'notTall': {
          'raw': `only screen and (min-height: 960px) and (min-width: 480px)`
        },
        'notSmallTablet': {
          'raw': 'only screen and (min-height: 1030px) and (min-width: 770px)'
        },
        '2md': '1024px',
        'lg': '1200px',
        'xl': '1380px',
        '2xl': '2000px',
        '3xl': '2360px'
      },
      fontFamily: {
        sans: ['Inter var', ...defaultTheme.fontFamily.sans]
      }
    },
  },
  plugins: [],
}