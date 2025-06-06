import tailwindcssMotion from "tailwindcss-motion";
import tailwindCssIntersect from "tailwindcss-intersect";

/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{html,js,svelte,ts}'],
  theme: {
    extend: {},
  },
  plugins: [
    tailwindcss-motion,
    tailwindCss-intersect
  ]
};


