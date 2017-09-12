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
    images = convert_images()

    # Attempt to run pandoc on markdown file
    import subprocess
    try:
        subprocess.call(
            ['pandoc', '-t', 'rst', '-o', 'README.rst', 'README-tmp.md']
        )
    except OSError:
        return LONG_DESCRIPTION

    # Attempt to load output
    try:
        readme = open(join(dirname(__file__), 'README.rst'))
    except IOError:
        return LONG_DESCRIPTION
    rst = readme.read()
    for i, imgrst in enumerate(images):
        rst = rst.replace("IMG%s" % i, imgrst)
    with open(join(dirname(__file__), 'README.rst'), 'w') as output:
        output.write(rst)
    return rst


def convert_images():
    """
    Convert HTML images to RST so they survive pandoc conversion
    """
    images = []
    try:
        readme = open('README.md')
    except IOError:
        return images

    with open('README-tmp.md', 'w') as output:
        img = None
        for row in readme:
            if not row.startswith('<img') and img is None:
                output.write(row)
                continue
            img = img or {}
            if 'alt=' in row:
                img['alt'] = row.replace('alt=', '').strip().strip('"')
            else:
                for part in row.replace('>', '').split(' '):
                    if '=' in part:
                        key, val = part.split('=')
                        img[key] = val.strip().strip('"')
            if '>' in row:
                src = img.pop('src')
                imgrst = "\n.. image:: %s\n" % src.replace('images/', 'images/320/')
                imgrst += "   :target: %s\n" % src
                for key, val in img.items():
                    val = val.replace('%', ' %')
                    if val.isdigit():
                        val += ' px'
                    imgrst += '   :%s: %s\n' % (key, val)
                output.write("IMG%s\n" % len(images))
                images.append(imgrst)
                img = None
    return images

setup(
    name='data-wizard',
    version='1.0.1',
    author='S. Andrew Sheppard',
    author_email='andrew@wq.io',
    url='https://wq.io/django-data-wizard',
    license='MIT',
    description=LONG_DESCRIPTION.strip(),
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
