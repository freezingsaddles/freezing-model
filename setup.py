# -*- coding: utf-8 -*-
import os.path
import re
import warnings

def simplify_ext(line):
    pattern = r"^.*egg=(.*)$"
    matches = re.findall(pattern, line)
    for match in matches:
        return match
    return line

# Thanks https://stackoverflow.com/a/39041067
def parse_requirements(filename):
    """ load requirements from a pip requirements file """
    lineiter = (line.strip() for line in open(filename))
    return [simplify_ext(line) for line in lineiter if line and not line.startswith("#")]

from setuptools import setup, find_packages

version = '0.5.13'

long_description = """
freezing-model is the database model and message definitions shared by freezing saddles components.
"""

install_reqs = parse_requirements(os.path.join(os.path.dirname(__file__), 'requirements.txt'))

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
    install_requires=install_reqs,
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
    ],
    zip_safe=True
)
