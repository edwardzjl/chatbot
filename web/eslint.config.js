import js from "@eslint/js";
import jsdoc from "eslint-plugin-jsdoc";
import react from "eslint-plugin-react";
import globals from "globals";


export default [
    js.configs.recommended,
    jsdoc.configs["flat/recommended"],
    {
        files: ["**/*.{js,jsx,mjs,cjs,ts,tsx}"],
        ignores: ["build/**/*", "node_modules/**/*"],
        languageOptions: {
            parserOptions: {
                ecmaFeatures: {
                    jsx: true,
                },
            },
            globals: {
                ...globals.browser,
            },
        },
        plugins: {
            jsdoc,
            react,
        },
        rules: {
            "jsdoc/require-description": "warn",
            "react/jsx-uses-react": "error",
            "react/jsx-uses-vars": "error",
        }
    }
];
