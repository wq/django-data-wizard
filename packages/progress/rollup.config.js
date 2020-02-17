import babel from 'rollup-plugin-babel';
import pkg from './package.json';

const name = pkg.name.replace(/^@wq/, ''),
    dir = `packages/${name}`;

const banner = `/*
 * ${pkg.name} ${pkg.version}
 * ${pkg.description}
 * (c) 2014-2020, S. Andrew Sheppard
 * https://wq.io/license
 */
`;

export default [
    // ESM & UMD
    {
        input: `${dir}/index.js`,
        plugins: [
            babel({
                configFile: false,
                presets: [
                    [
                        '@babel/preset-env',
                        {
                            targets: {
                                esmodules: true
                            }
                        }
                    ]
                ]
            })
        ],
        external: ['jquery'],
        output: [
            {
                banner,
                file: `${dir}/dist/index.es.js`,
                format: 'esm',
                exports: 'named'
            },
            {
                name,
                exports: 'named',
                globals: { jquery: '$' },
                banner,
                file: `${dir}/dist/${name}.js`,
                format: 'umd',
                sourcemap: true,
                indent: false
            }
        ]
    },
    // CJS
    {
        input: `${dir}/index.js`,
        plugins: [
            babel({
                configFile: false,
                presets: [
                    [
                        '@babel/preset-env',
                        {
                            targets: {
                                node: 8
                            }
                        }
                    ]
                ]
            })
        ],
        external: ['jquery'],
        output: {
            banner: banner,
            file: `${dir}/dist/index.js`,
            format: 'cjs',
            exports: 'named'
        }
    }
];
