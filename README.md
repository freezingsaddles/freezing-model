# freezing-model
SQLAlchemy model for Freezing Saddles database
==============================================

This package uses [SQLAlchemy](https://www.sqlalchemy.org/) to model the
database tables for the Freezing Saddles database. It uses
[alembic](ihttps://pypi.org/project/alembic/) to perform database migrations. 

Usage
-----
This is intended for use with the other
[Freezing Saddles projects](https://github.org/freezingsaddles/) projects
including [freezing-web](https://github.org/freezingsaddles/freezing-web).
When used from `freezing-web` it will retrieve its database configuration
from the [Flask](http://flask.pocoo.org/) application configuration. When
used from the command line, it will take its configuration from the
[alembic.ini](alembic.ini) file and optionally from the environment.

You can override the database URL by specifying a `SQLALCHEMY_URL` environment
variable, for example:

    export SQLALCHEMY_URL='mysql+pymysql://user:password@127.0.0.1/freezing?charset=utf8mb4&binary_prefix=true'
    PYTHONPATH=$(pwd) alembic current
    PYTHONPATH=$(pwd) alembic upgrade head

### Coding standards

The `freezing-web` code is intended to be [PEP-8](https://www.python.org/dev/peps/pep-0008/) compliant. Code formatting is done with [black](https://black.readthedocs.io/en/stable/) and can be linted with [flake8](http://flake8.pycqa.org/en/latest/). See the [.flake8](.flake8) file and install the test dependencies to get these tools (`pip install -r test-requirements.txt`).

