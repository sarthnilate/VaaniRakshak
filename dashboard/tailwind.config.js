/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        // VaaniRakshak status semantics - Design.md section 3.
        // Do not use these as decoration; they communicate risk state only.
        safe: "#22c55e",
        low: "#3b82f6",
        medium: "#f59e0b",
        high: "#f97316",
        critical: "#ef4444",
      },
    },
  },
  plugins: [],
};
