#!/usr/bin/env python
# -*- coding: utf-8 -*-


from setuptools import (
    find_packages,
    setup,
    )
from pip.req import parse_requirements

with open('README.md') as readme_file:
    README = readme_file.read()

with open('CHANGES.txt') as history_file:
    CHANGES = history_file.read().replace('.. :changelog:', '')

requirements = parse_requirements('requirements.txt')

test_requirements = parse_requirements('test-requirements.txt')

setup(
    name='jujulib',
    version='0.0.1',
    description='Jujulib is a python library designed to automate Juju.',
    long_description=README + '\n\n' + CHANGES,
    author='Mark Ramm-Christensen',
    author_email='mark.ramm-christensen@canonical.com',
    url='https://github.com/juju/jujulib',
    packages=find_packages('.'),
    install_requires=[str(ir.req) for ir in requirements],
    license='LGPL',
    zip_safe=False,
    keywords='jujulib juju',
    classifiers=[
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python',
    ],
    test_suite='tests',
    tests_require=[str(ir.req) for ir in test_requirements]
)
