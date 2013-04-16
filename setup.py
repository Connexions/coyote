# -*- coding: utf-8 -*-

"""
Copyright (C) 2013 Rice University

This software is subject to the provisions of the GNU AFFERO GENERAL PUBLIC LICENSE Version 3.0 (AGPL).  
See LICENSE.txt for details.
"""

import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = os.path.join(here, 'README.rst')

install_requirements = [
    'pybit',
    'pika',
    'jsonpickle',
    'requests',
    ]
test_requirements = [
    'mock',
    ]

setup(
    name='rbit',
    version='1.0',
    author="Connexions/Rhaptos Team",
    author_email="info@cnx.org",
    description='Rhaptos PyBit client implementation',
    long_description=open(README).read(),
    url='https://github.com/connexions/rbit',
    license='GPL2',  # See also LICENSE.txt
    packages=find_packages(),
    include_package_data=True,
    install_requires=install_requirements,
    extras_require={
        'tests': test_requirements,
        },
    entry_points = """\
    [console_scripts]
    rbit = rbit:main
    """,
    )
