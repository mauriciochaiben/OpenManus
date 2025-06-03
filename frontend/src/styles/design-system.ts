/**
 * Flowith-inspired Design System
 * Colors, typography, spacing, and component styles
 */

export const colors = {
  // Primary palette inspired by Flowith
  primary: {
    50: "#f0f9ff",
    100: "#e0f2fe",
    200: "#bae6fd",
    300: "#7dd3fc",
    400: "#38bdf8",
    500: "#0ea5e9",
    600: "#0284c7",
    700: "#0369a1",
    800: "#075985",
    900: "#0c4a6e",
  },

  // Accent colors
  accent: {
    purple: "#8b5cf6",
    violet: "#a855f7",
    indigo: "#6366f1",
    blue: "#3b82f6",
    cyan: "#06b6d4",
    teal: "#14b8a6",
    emerald: "#10b981",
  },

  // Semantic colors
  semantic: {
    success: "#10b981",
    warning: "#f59e0b",
    error: "#ef4444",
    info: "#3b82f6",
  },

  // Neutral palette
  neutral: {
    50: "#fafafa",
    100: "#f5f5f5",
    200: "#e5e5e5",
    300: "#d4d4d4",
    400: "#a3a3a3",
    500: "#737373",
    600: "#525252",
    700: "#404040",
    800: "#262626",
    900: "#171717",
  },

  // Background variations
  background: {
    primary: "#ffffff",
    secondary: "#f8fafc",
    tertiary: "#f1f5f9",
    accent: "#f0f9ff",
    dark: "#0f172a",
  },

  // Border colors
  border: {
    light: "#e2e8f0",
    medium: "#cbd5e1",
    dark: "#94a3b8",
  },

  // Text colors
  text: {
    primary: "#0f172a",
    secondary: "#475569",
    tertiary: "#64748b",
    inverse: "#ffffff",
    muted: "#94a3b8",
  },
};

export const typography = {
  fontFamily: {
    sans: [
      "Inter",
      "-apple-system",
      "BlinkMacSystemFont",
      "Segoe UI",
      "Roboto",
      "sans-serif",
    ],
    mono: ["JetBrains Mono", "Menlo", "Monaco", "Consolas", "monospace"],
  },

  fontSize: {
    xs: "0.75rem", // 12px
    sm: "0.875rem", // 14px
    base: "1rem", // 16px
    lg: "1.125rem", // 18px
    xl: "1.25rem", // 20px
    "2xl": "1.5rem", // 24px
    "3xl": "1.875rem", // 30px
    "4xl": "2.25rem", // 36px
    "5xl": "3rem", // 48px
  },

  fontWeight: {
    light: 300,
    normal: 400,
    medium: 500,
    semibold: 600,
    bold: 700,
  },

  lineHeight: {
    tight: 1.25,
    normal: 1.5,
    relaxed: 1.75,
  },
};

export const spacing = {
  0: "0",
  1: "0.25rem", // 4px
  2: "0.5rem", // 8px
  3: "0.75rem", // 12px
  4: "1rem", // 16px
  5: "1.25rem", // 20px
  6: "1.5rem", // 24px
  8: "2rem", // 32px
  10: "2.5rem", // 40px
  12: "3rem", // 48px
  16: "4rem", // 64px
  20: "5rem", // 80px
  24: "6rem", // 96px
};

export const borderRadius = {
  none: "0",
  sm: "0.125rem", // 2px
  base: "0.25rem", // 4px
  md: "0.375rem", // 6px
  lg: "0.5rem", // 8px
  xl: "0.75rem", // 12px
  "2xl": "1rem", // 16px
  "3xl": "1.5rem", // 24px
  full: "9999px",
};

export const shadows = {
  sm: "0 1px 2px 0 rgb(0 0 0 / 0.05)",
  base: "0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)",
  md: "0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)",
  lg: "0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)",
  xl: "0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)",
  "2xl": "0 25px 50px -12px rgb(0 0 0 / 0.25)",
  inner: "inset 0 2px 4px 0 rgb(0 0 0 / 0.05)",
  glow: "0 0 20px rgb(59 130 246 / 0.3)",
};

export const transitions = {
  fast: "150ms cubic-bezier(0.4, 0, 0.2, 1)",
  normal: "200ms cubic-bezier(0.4, 0, 0.2, 1)",
  slow: "300ms cubic-bezier(0.4, 0, 0.2, 1)",
  bounce: "200ms cubic-bezier(0.68, -0.55, 0.265, 1.55)",
};

// Component-specific styles
export const components = {
  card: {
    background: colors.background.primary,
    border: `1px solid ${colors.border.light}`,
    borderRadius: borderRadius.xl,
    boxShadow: shadows.sm,
    padding: spacing[6],
    transition: transitions.normal,

    hover: {
      borderColor: colors.border.medium,
      boxShadow: shadows.md,
      transform: "translateY(-1px)",
    },

    active: {
      borderColor: colors.primary[500],
      boxShadow: `0 0 0 3px ${colors.primary[100]}`,
    },
  },

  button: {
    primary: {
      background: `linear-gradient(135deg, ${colors.primary[500]} 0%, ${colors.primary[600]} 100%)`,
      color: colors.text.inverse,
      border: "none",
      borderRadius: borderRadius.lg,
      fontSize: typography.fontSize.sm,
      fontWeight: typography.fontWeight.medium,
      padding: `${spacing[3]} ${spacing[6]}`,
      boxShadow: shadows.sm,
      transition: transitions.normal,

      hover: {
        background: `linear-gradient(135deg, ${colors.primary[600]} 0%, ${colors.primary[700]} 100%)`,
        boxShadow: shadows.md,
        transform: "translateY(-1px)",
      },
    },

    secondary: {
      background: colors.background.primary,
      color: colors.text.primary,
      border: `1px solid ${colors.border.medium}`,
      borderRadius: borderRadius.lg,
      fontSize: typography.fontSize.sm,
      fontWeight: typography.fontWeight.medium,
      padding: `${spacing[3]} ${spacing[6]}`,
      transition: transitions.normal,

      hover: {
        background: colors.background.secondary,
        borderColor: colors.border.dark,
      },
    },
  },

  input: {
    background: colors.background.primary,
    border: `1px solid ${colors.border.light}`,
    borderRadius: borderRadius.lg,
    fontSize: typography.fontSize.sm,
    padding: `${spacing[3]} ${spacing[4]}`,
    transition: transitions.normal,

    focus: {
      borderColor: colors.primary[500],
      boxShadow: `0 0 0 3px ${colors.primary[100]}`,
      outline: "none",
    },

    error: {
      borderColor: colors.semantic.error,
      boxShadow: `0 0 0 3px rgba(239, 68, 68, 0.1)`,
    },
  },

  sidebar: {
    background: colors.background.primary,
    borderRight: `1px solid ${colors.border.light}`,
    width: "280px",

    item: {
      padding: `${spacing[3]} ${spacing[4]}`,
      borderRadius: borderRadius.lg,
      margin: `0 ${spacing[2]} ${spacing[1]} ${spacing[2]}`,
      transition: transitions.normal,

      hover: {
        background: colors.background.secondary,
      },

      active: {
        background: colors.primary[50],
        color: colors.primary[700],
        fontWeight: typography.fontWeight.medium,
      },
    },
  },

  modal: {
    overlay: {
      background: "rgba(0, 0, 0, 0.5)",
      backdropFilter: "blur(4px)",
    },

    content: {
      background: colors.background.primary,
      borderRadius: borderRadius["2xl"],
      boxShadow: shadows["2xl"],
      border: "none",
      maxWidth: "600px",
      width: "90vw",
    },
  },
};

// CSS-in-JS utilities
export const createGradient = (direction: string, ...colors: string[]) => {
  return `linear-gradient(${direction}, ${colors.join(", ")})`;
};

export const createBoxShadow = (color: string, opacity: number = 0.1) => {
  return `0 4px 6px -1px rgba(${color}, ${opacity}), 0 2px 4px -2px rgba(${color}, ${
    opacity * 0.5
  })`;
};

export const createGlassEffect = (opacity: number = 0.1) => ({
  background: `rgba(255, 255, 255, ${opacity})`,
  backdropFilter: "blur(10px)",
  border: `1px solid rgba(255, 255, 255, ${opacity * 2})`,
});

// Responsive breakpoints
export const breakpoints = {
  xs: "480px",
  sm: "640px",
  md: "768px",
  lg: "1024px",
  xl: "1280px",
  "2xl": "1536px",
};

// Animation keyframes
export const animations = {
  fadeIn: `
    @keyframes fadeIn {
      from { opacity: 0; }
      to { opacity: 1; }
    }
  `,
  slideUp: `
    @keyframes slideUp {
      from { transform: translateY(20px); opacity: 0; }
      to { transform: translateY(0); opacity: 1; }
    }
  `,
  slideDown: `
    @keyframes slideDown {
      from { transform: translateY(-20px); opacity: 0; }
      to { transform: translateY(0); opacity: 1; }
    }
  `,
  scaleIn: `
    @keyframes scaleIn {
      from { transform: scale(0.95); opacity: 0; }
      to { transform: scale(1); opacity: 1; }
    }
  `,
  pulse: `
    @keyframes pulse {
      0%, 100% { opacity: 1; }
      50% { opacity: 0.5; }
    }
  `,
  spin: `
    @keyframes spin {
      from { transform: rotate(0deg); }
      to { transform: rotate(360deg); }
    }
  `,
};

export default {
  colors,
  typography,
  spacing,
  borderRadius,
  shadows,
  transitions,
  components,
  breakpoints,
  animations,
  createGradient,
  createBoxShadow,
  createGlassEffect,
};
