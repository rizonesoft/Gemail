// ESLint flat config for Gemail. `office-addin-lint` (npm run lint) uses this
// file when it exists; the old .eslintrc.json was read by nothing (ESLint 9).
//
// Scope: office-addin-lint lints src/**/*.{ts,tsx,js,jsx}; everything there is
// TypeScript. `no-undef` is off for TypeScript because the compiler already
// checks every name (typescript-eslint's guidance:
// https://typescript-eslint.io/troubleshooting/faqs/eslint#i-get-errors-from-the-no-undef-rule-about-global-variables-not-being-defined-even-though-there-are-no-typescript-errors),
// so no globals package is needed.
import officeAddins from "eslint-plugin-office-addins";
import tsParser from "@typescript-eslint/parser";
import tsPlugin from "@typescript-eslint/eslint-plugin";

export default [
  { ignores: ["dist/**", "build/**", "lib/**", "node_modules/**", "tools/**"] },
  ...officeAddins.configs.recommended,
  ...tsPlugin.configs["flat/recommended"],
  {
    files: ["**/*.ts", "**/*.tsx"],
    plugins: { "office-addins": officeAddins },
    languageOptions: {
      parser: tsParser,
      ecmaVersion: 2022,
      sourceType: "module",
    },
    rules: {
      "no-undef": "off",
      // Carried from .eslintrc.json (its two deliberate rules).
      "@typescript-eslint/no-unused-vars": ["error", { argsIgnorePattern: "^_" }],
      "@typescript-eslint/no-explicit-any": "warn",
    },
  },
];
