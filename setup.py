# -*- coding: utf-8 -*-
from __future__ import absolute_import

import os
import sys
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
CHANGES = open(os.path.join(here, 'CHANGES.rst')).read()

class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = ['backup_utils']
        self.test_suite = True
    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)

install_requires = []

setup(
    name="backup-utils",
    version='0.1rc1',
    description='Jeff’s backup helpers',
    long_description=README + '\n\n' + CHANGES,
    author='Jeff Dairiki',
    author_email='dairiki@dairiki.org',
    url='git@github.com:dairiki/backup-utils.git',
    license='BSD',
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        ],
    packages=find_packages(),
    zip_safe=True,
    include_package_data=True,
    install_requires=install_requires,
    tests_require=[
        'pytest',
        ],
    cmdclass={
        'test': PyTest,
        },
    entry_points={
        'console_scripts': [
            'tarsnap-clean = backup_utils.tarsnap:tarsnap_clean',
            ],
        },
    )
