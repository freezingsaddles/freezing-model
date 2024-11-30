# -*- coding: utf-8 -*-
from setuptools import setup

version = "0.8.6"

long_description = """
freezing-model is the database model and message definitions
shared by Freezing Saddles components.
"""

install_reqs = [
    "SQLAlchemy==1.3.24",
    "GeoAlchemy",
    "PyMySQL",
    "alembic==0.9.7",
    "colorlog",
    "marshmallow",
    "marshmallow-enum",
    "pytz",
]

setup(
    name="freezing-model",
    version=version,
    author="Hans Lellelid",
    author_email="hans@xmpl.org",
    url="http://github.com/freezingsaddles/freezing-model",
    license="Apache",
    description="Freezing Saddles database and messaging models.",
    long_description=long_description,
    packages=["freezing.model", "freezing.model.msg"],
    include_package_data=True,
    package_data={"freezing.model": ["migrations/*"]},
    install_requires=install_reqs,
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
    ],
    zip_safe=True,
)
