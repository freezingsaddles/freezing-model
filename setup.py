# -*- coding: utf-8 -*-
import os.path
import re
import warnings

# Ugh, pip 10 is backward incompatible, but there is a workaround:
# Thanks Stack Overflow https://stackoverflow.com/a/49867265
try: # for pip >= 10
    from pip._internal.req import parse_requirements
except ImportError: # for pip <= 9.0.3
    from pip.req import parse_requirements

from setuptools import setup, find_packages

version = '0.3.3'

long_description = """
freezing-model is the database model and message definitions shared by freezing saddles components.
"""

# parse_requirements() returns generator of pip.req.InstallRequirement objects
install_reqs = parse_requirements(os.path.join(os.path.dirname(__file__), 'requirements.txt'), session=False)

# reqs is a list of requirement
# e.g. ['django==1.5.1', 'mezzanine==1.4.6']
# This started failing on some Docker builds, for example: https://hub.docker.com/repository/registry-1.docker.io/freezingsaddles/freezing-web/builds/3b84dc71-e91b-4e7e-af3f-3eb41b40d5b8
# Thanks Mehant Kammakomati and Stack Overflow for the fix: https://stackoverflow.com/a/62127548
try:
    reqs = [str(ir.req) for ir in install_reqs]
except:
    reqs = [str(ir.requirement) for ir in install_reqs]

setup(
    name='freezing-model',
    version=version,
    author='Hans Lellelid',
    author_email='hans@xmpl.org',
    url='http://github.com/freezingsaddles/freezing-model',
    license='Apache',
    description='Freezing Saddles database and messaging models.',
    long_description=long_description,
    packages=['freezing.model', 'freezing.model.msg'],
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
