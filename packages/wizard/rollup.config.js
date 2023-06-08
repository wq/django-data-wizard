import pkg from './package.json' assert { type: 'json' };
import wq from '@wq/rollup-plugin';
import babel from '@rollup/plugin-babel';
import resolve from '@rollup/plugin-node-resolve';
import replace from '@rollup/plugin-replace';
import terser from '@rollup/plugin-terser';

const banner = `/*
 * ${pkg.name} ${pkg.version}
 * ${pkg.description}
 * (c) 2014-2021, S. Andrew Sheppard
 * https://wq.io/license
 */
`;

const dir = `packages/${pkg.name.replace('@wq/', '')}`;

const config = {
        input: `${dir}/src/index.js`,
        plugins: [
            wq(),
            babel({
                plugins: [
                    '@babel/transform-react-jsx',
                    [
                        'babel-plugin-direct-import',
                        { modules: ['@mui/icons-material'] },
                    ],
                ],
                babelHelpers: 'inline',
            }),
            resolve(),
            terser({ keep_fnames: /^([A-Z]|use[A-Z])/ }), // Preserve component & hook names
        ],
        output: {
            file: `${dir}/dist/index.js`,
            banner,
            format: 'esm',
            sourcemap: true,
        },
    },
    replaceConfig = {
        'process.env.NODE_ENV': '"production"',
        delimiters: ['', ''],
        preventAssignment: true,
    };

export default [
    // @wq/app plugin (npm main)
    {
        ...config,
        external: [
            'react',
            'formik',
            'prop-types',
            '@wq/react',
            '@wq/material',
            '@wq/progress',
            '@mui/material',
            '@mui/icons-material',
        ],
        plugins: [
            babel({
                plugins: ['@babel/transform-react-jsx'],
                babelHelpers: 'inline',
            }),
        ],
    },
    // wq.app staticfiles plugin (for data-wizard python package)
    {
        ...config,
        plugins: [replace(replaceConfig), ...config.plugins],
        output: {
            ...config.output,
            file: 'data_wizard/static/app/js/wizard.js',
            sourcemapPathTransform(path) {
                return path.replace('../../../../', 'django-data-wizard/');
            },
        },
    },
    // wq.app staticfiles plugin (unpkg)
    {
        ...config,
        plugins: [
            replace({
                ...replaceConfig,
                './wq.js': 'https://unpkg.com/wq',
            }),
            ...config.plugins,
        ],
        output: {
            ...config.output,
            file: `${dir}/dist/index.unpkg.js`,
            sourcemapPathTransform(path) {
                return path.replace('./', 'wq/wizard/');
            },
        },
    },
];
