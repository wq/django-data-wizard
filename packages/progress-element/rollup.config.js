import babel from '@rollup/plugin-babel';
import resolve from '@rollup/plugin-node-resolve';
import pkg from './package.json' assert { type: 'json' };

const name = pkg.name.replace(/^@wq/, ''),
    dir = `packages/${name}`;

const banner = `/*
 * ${pkg.name} ${pkg.version}
 * ${pkg.description}
 * (c) 2014-2021, S. Andrew Sheppard
 * https://wq.io/license
 */
`;

export default [
    // UMD
    {
        input: `${dir}/src/progress.js`,
        plugins: [
            resolve(),
            babel({
                configFile: false,
                presets: [
                    [
                        '@babel/preset-env',
                        {
                            targets: {
                                esmodules: true,
                            },
                        },
                    ],
                ],
            }),
        ],
        external: ['jquery'],
        output: [
            {
                name,
                exports: 'named',
                globals: { jquery: '$' },
                banner,
                file: `data_wizard/static/data_wizard/js/${name}.js`,
                format: 'umd',
                sourcemap: true,
                indent: false,
                sourcemapPathTransform(path) {
                    return path.replace('../../../../', 'django-data-wizard/');
                },
            },
        ],
    },
];
