from os.path import join, dirname
from setuptools import setup

LONG_DESCRIPTION = """
Reference implementation of the ERAV model, an extention to EAV with support for maintaining multiple versions of an entity with different provenance.
"""

def long_description():
    """Return long description from README.rst if it's present
    because it doesn't get installed."""
    try:
        return open(join(dirname(__file__), 'README.rst')).read()
    except IOError:
        return LONG_DESCRIPTION

setup(
    name = 'vera',
    version = '0.4.0',
    author='S. Andrew Sheppard',
    author_email='andrew@wq.io',
    url='http://wq.io/vera',
    license='MIT',
    description='Implementation of the ERAV data integration model',
    long_description=long_description(),
    install_requires=['wq==0.4.0', 'django-celery', 'johnny-cache', 'django-redis-cache', 'Pillow'],
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: JavaScript',
        'Programming Language :: Python :: 2.7',
        'Framework :: Django',
        'Topic :: Scientific/Engineering :: GIS',
        'Topic :: Database :: Database Engines/Servers',
    ]
)
