import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{js,ts,jsx,tsx,mdx}", "./components/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        bg: "var(--bg)",
        panel: "var(--panel)",
        "panel-raised": "var(--panel-raised)",
        hairline: "var(--hairline)",
        "hairline-bright": "var(--hairline-bright)",
        text: "var(--text)",
        "text-muted": "var(--text-muted)",
        "text-faint": "var(--text-faint)",
        amber: "var(--amber)",
        "amber-dim": "var(--amber-dim)",
        teal: "var(--teal)",
        "teal-dim": "var(--teal-dim)",
        coral: "var(--coral)",
        "coral-dim": "var(--coral-dim)",
        "blue-signal": "var(--blue-signal)",
      },
      fontFamily: {
        sans: ["var(--font-ibm-plex-sans)", "sans-serif"],
        mono: ["var(--font-ibm-plex-mono)", "monospace"],
      },
    },
  },
  plugins: [],
};

export default config;
