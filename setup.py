# -*- coding: utf-8 -*-
import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = os.path.join(here, 'README.rst')
CHANGES = os.path.join(here, 'CHANGES.rst')

install_requirements = [
    'pika',
    'requests',
    # PyBit and dependencies
    'pybit',
    'psycopg2',
    'amqplib',
    'jsonpickle',
    ]
test_requirements = [
    ]

setup(
    name='coyote',
    version='0.1',
    author="Connexions/Rhaptos Team",
    author_email="info@cnx.org",
    description='',
    long_description='\n'.join([open(README).read(), open(CHANGES).read()]),
    url='https://github.com/connexions/coyote',
    license='AGPL',  # See also LICENSE.txt
    packages=find_packages(),
    include_package_data=True,
    install_requires=install_requirements,
    extras_require={
        'tests': test_requirements,
        },
    entry_points = """\
    [console_scripts]
    coyote = coyote:main
    """,
    )
