from setuptools import setup
from setuptools.command.build_py import build_py
import subprocess
import shutil
import warnings


LONG_DESCRIPTION = """
Interactive web-based wizard for importing structured data into Django models.
"""

JS_FILES = [
    'packages/progress/dist/progress.js',
    'packages/progress/dist/progress.js.map',
]


class BuildJS(build_py):
    def run(self):
        try:
            subprocess.check_call(['npm', 'install'])
            subprocess.check_call(['npm', 'run', 'build'])
        except BaseException as e:
            warnings.warn("Skipping JS build: {}".format(e))
        else:
            for path in JS_FILES:
                shutil.copy(path, 'data_wizard/static/data_wizard/js')
        super().run()


def readme():
    try:
        readme = open('README.md')
    except IOError:
        return LONG_DESCRIPTION
    else:
        return readme.read()


setup(
    name='data-wizard',
    use_scm_version=True,
    author='S. Andrew Sheppard',
    author_email='andrew@wq.io',
    url='https://github.com/wq/django-data-wizard',
    license='MIT',
    description=LONG_DESCRIPTION.strip(),
    long_description=readme(),
    long_description_content_type='text/markdown',
    packages=[
        'data_wizard',
        'data_wizard.backends',
        'data_wizard.management',
        'data_wizard.management.commands',
        'data_wizard.migrations',
        'data_wizard.sources',
        'data_wizard.sources.migrations',
    ],
    package_data={
        'data_wizard': [
            'mustache/*.html',
            'templates/data_wizard/*.html',
            'static/data_wizard/js/*.js',
            'static/data_wizard/css/*.css',
        ]
    },
    install_requires=[
        'djangorestframework',
        'itertable',
        'natural-keys',
        'html-json-forms',
        'python-dateutil'
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: JavaScript',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Framework :: Django',
        'Framework :: Django :: 1.8',
        'Framework :: Django :: 1.11',
        'Framework :: Django :: 2.0',
        'Framework :: Django :: 2.1',
        'Framework :: Django :: 2.2',
        'Framework :: Django :: 3.0',
        'Topic :: Scientific/Engineering :: GIS',
        'Topic :: Database :: Database Engines/Servers',
    ],
    test_suite='tests',
    setup_requires=[
        'setuptools_scm',
    ],
    cmdclass={
       'build_py': BuildJS
    },
)
