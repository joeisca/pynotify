#!/usr/bin/env python

# Author: Forest Bond
# This file is in the public domain.

from distutils.core import Extension
import os
import subprocess
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'modules'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from setuplib import setup


def get_version(release_file):
    try:
        f = open(release_file, 'r')
        try:
            return f.read().strip()
        finally:
            f.close()
    except (IOError, OSError):
        try:
            output = subprocess.check_output(['bzr', 'revno'])
            return 'bzr' + output.strip()
        except Exception:
            pass
    return 'unknown'


version = get_version('release')

setup(
    name='pynotify',
    distinfo_module='inotifyx.distinfo',
    version=version,
    description='Simple Linux inotify bindings',
    author='Forest Bond',
    author_email='forest@forestbond.com',
    url='https://launchpad.net/inotifyx/',
    packages=['inotifyx'],
    entry_points={
        "console_scripts": [
            "pynotify=inotifyx:main",
        ]
    },
    ext_modules=[
        Extension(
            'inotifyx.binding',
            sources=[os.path.join('inotifyx', 'binding.c')],
        ),
    ],
)
