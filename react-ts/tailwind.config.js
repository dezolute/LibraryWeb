/** @type {import('@tailwindcss/postcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  important: true, // это позволит Tailwind переопределять стили Ant Design при необходимости
  theme: {
    extend: {
      colors: {
        primary: '#1890ff',
      },
      spacing: {
        '18': '4.5rem',
        '112': '28rem',
        '128': '32rem',
      },
    },
  },
  corePlugins: {
    preflight: false, // отключаем сброс стилей, так как мы используем Ant Design
  },
}