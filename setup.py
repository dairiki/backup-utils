# -*- coding: utf-8 -*-
from __future__ import absolute_import

import sys
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

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
    version='0.1',
    description='Jeff’s backup helpers',
    #long_description=,
    author='Jeff Dairiki',
    author_email='dairiki@dairiki.org',
    #url=
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
