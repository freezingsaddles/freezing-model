# -*- coding: utf-8 -*-
import os.path
import re
import warnings

from pip.req import parse_requirements
from setuptools import setup, find_packages

version = '0.1.1'

long_description = """
freezing-model is the database model definition shared by freezing saddles components.
"""

# parse_requirements() returns generator of pip.req.InstallRequirement objects
install_reqs = parse_requirements(os.path.join(os.path.dirname(__file__), 'requirements.txt'), session=False)

# reqs is a list of requirement
# e.g. ['django==1.5.1', 'mezzanine==1.4.6']
reqs = [str(ir.req) for ir in install_reqs]

setup(
    name='freezing-model',
    version=version,
    author='Hans Lellelid',
    author_email='hans@xmpl.org',
    url='http://github.com/hozn/freezing-model',
    license='Apache',
    description='Freezing Saddles database model.',
    long_description=long_description,
    packages=['freezing.model'],
    include_package_data=True,
    package_data={'freezing.model': ['migrations/*']},
    install_requires=reqs,
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
    ],
    zip_safe=True
)
