// color design tokens export
export const colorTokens = {
  grey: {
    0: "#FFFFFF",
    10: "#F9FAFB",
    50: "#F3F4F6",
    100: "#E5E7EB",
    200: "#D1D5DB",
    300: "#9CA3AF",
    400: "#6B7280",
    500: "#4B5563",
    600: "#374151",
    700: "#1F2937",
    800: "#111827",
    900: "#030712",
    1000: "#000000",
  },
  primary: {
    50: "#EEF2FF",
    100: "#E0E7FF",
    200: "#C7D2FE",
    300: "#A5B4FC",
    400: "#818CF8",
    500: "#0A66C2", // LinkedIn Blue
    600: "#004182",
    700: "#002244",
    800: "#001122",
    900: "#000811",
  },
};

// mui theme settings
export const themeSettings = (mode) => {
  return {
    palette: {
      mode: mode,
      ...(mode === "dark"
        ? {
            // palette values for dark mode
            primary: {
              dark: colorTokens.primary[200],
              main: colorTokens.primary[400],
              light: colorTokens.primary[800],
            },
            neutral: {
              dark: colorTokens.grey[100],
              main: colorTokens.grey[200],
              mediumMain: colorTokens.grey[300],
              medium: colorTokens.grey[400],
              light: colorTokens.grey[700],
            },
            background: {
              default: colorTokens.grey[900],
              alt: colorTokens.grey[800],
            },
          }
        : {
            // palette values for light mode
            primary: {
              dark: colorTokens.primary[700],
              main: colorTokens.primary[500],
              light: colorTokens.primary[50],
            },
            neutral: {
              dark: colorTokens.grey[700],
              main: colorTokens.grey[500],
              mediumMain: colorTokens.grey[400],
              medium: colorTokens.grey[300],
              light: colorTokens.grey[50],
            },
            background: {
              default: colorTokens.grey[10],
              alt: colorTokens.grey[0],
            },
          }),
    },
    typography: {
      fontFamily: ["Inter", "Rubik", "sans-serif"].join(","),
      fontSize: 14,
      h1: {
        fontFamily: ["Inter", "Rubik", "sans-serif"].join(","),
        fontSize: 40,
        fontWeight: 700,
      },
      h2: {
        fontFamily: ["Inter", "Rubik", "sans-serif"].join(","),
        fontSize: 32,
        fontWeight: 700,
      },
      h3: {
        fontFamily: ["Inter", "Rubik", "sans-serif"].join(","),
        fontSize: 24,
        fontWeight: 600,
      },
      h4: {
        fontFamily: ["Inter", "Rubik", "sans-serif"].join(","),
        fontSize: 20,
        fontWeight: 600,
      },
      h5: {
        fontFamily: ["Inter", "Rubik", "sans-serif"].join(","),
        fontSize: 16,
        fontWeight: 600,
      },
      h6: {
        fontFamily: ["Inter", "Rubik", "sans-serif"].join(","),
        fontSize: 14,
        fontWeight: 600,
      },
    },
    shape: {
      borderRadius: 8,
    },
  };
};