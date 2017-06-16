from os.path import join, dirname
from setuptools import setup

LONG_DESCRIPTION = """
Interactive web-based wizard to facilitate importing structured data into Django models.
"""


def parse_markdown_readme():
    """
    Convert README.md to RST via pandoc, and load into memory
    (fallback to LONG_DESCRIPTION on failure)
    """
    # Attempt to run pandoc on markdown file
    import subprocess
    try:
        subprocess.call(
            ['pandoc', '-t', 'rst', '-o', 'README.rst', 'README.md']
        )
    except OSError:
        return LONG_DESCRIPTION

    # Attempt to load output
    try:
        readme = open(join(dirname(__file__), 'README.rst'))
    except IOError:
        return LONG_DESCRIPTION
    return readme.read()


setup(
    name='data-wizard',
    version='1.0.0rc1',
    author='S. Andrew Sheppard',
    author_email='andrew@wq.io',
    url='https://wq.io/django-data-wizard',
    license='MIT',
    description='Django Data Wizard',
    long_description=parse_markdown_readme(),
    packages=[
        'data_wizard',
        'data_wizard.migrations',
    ],
    package_data={
        'data_wizard': [
            'mustache/*.*',
        ]
    },
    install_requires=[
        'wq.io',
        'natural-keys',
        'html-json-forms',
        'celery',
        'redis',
        'python-dateutil'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
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
        'Framework :: Django',
        'Framework :: Django :: 1.8',
        'Framework :: Django :: 1.9',
        'Framework :: Django :: 1.10',
        'Framework :: Django :: 1.11',
        'Topic :: Scientific/Engineering :: GIS',
        'Topic :: Database :: Database Engines/Servers',
    ],
    test_suite='tests',
    tests_require=[
        'psycopg2',
    ],
)
