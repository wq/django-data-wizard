import js from "@eslint/js";
import globals from "globals";
import pluginReact from "eslint-plugin-react";
import { defineConfig } from "eslint/config";

export default defineConfig([
    {
        ignores: [
            "docs/.cache/**",
            "docs/public/**",
            "data_wizard/static/**",
            "docs/js/**",
        ],
    },
    {
        files: ["**/*.{js,mjs,cjs,jsx}"],
        plugins: { js },
        extends: ["js/recommended"],
        languageOptions: {
            globals: {
                ...globals.browser,
                ...globals.jest,
                ...globals.node,
            },
        },
        rules: {
            "react/prop-types": [
                2,
                {
                    skipUndeclared: true,
                },
            ],
        },
    },
    pluginReact.configs.flat.recommended,
]);
