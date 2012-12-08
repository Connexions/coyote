# -*- coding: utf-8 -*-
import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = os.path.join(here, 'README.rst')

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
    install_requires=[
        'pybit',
        'pika',
        ],
    entry_points = """\
    """,
    )
