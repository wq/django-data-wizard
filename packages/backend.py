from setuptools.build_meta import *
from setuptools_scm import get_version
import warnings

import builder


default_build_sdist = build_sdist
default_build_wheel = build_wheel


class UnsupportedOperation(Exception):
    pass


def ensure_js_build(autobuild=False):
    if builder.ready():
        return
    builder.log_hash()
    version = get_version()
    if ".dev" in version:
        warnings.warn(
            "Speed up dev builds by running python -m packages.builder first."
        )
        if autobuild:
            builder.build()
    else:
        raise UnsupportedOperation(
            "Run python -m packages.builder and commit before releasing."
        )


def build_sdist(*args, **kwargs):
    ensure_js_build(False)
    return default_build_sdist(*args, **kwargs)


def build_wheel(*args, **kwargs):
    ensure_js_build(True)
    return default_build_wheel(*args, **kwargs)
