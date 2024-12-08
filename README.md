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
The `freezing-model` code is intended to be [PEP-8](https://www.python.org/dev/peps/pep-0008/) compliant. Code formatting is done with [black](https://black.readthedocs.io/en/stable/) and can be linted with [flake8](http://flake8.pycqa.org/en/latest/). See the [.flake8](.flake8) file and install the test dependencies to get these tools (`pip install -r test-requirements.txt`).

Useful Queries
--------------
(TODO: This is probably not the best place for this documentation, but I'm not sure where else to put it)

Beyond the model definitions there are a few other useful SQL utilities and queries that can help in operations:

The script [bin/registrants.py](bin/registrants.py), given a CSV export from the WordPress registration site for Freezing Saddles, can generate a `registrants` table in the `freezing` database that is useful for determining who has registered but has not authorized properly in the database.

These queries can find users who need to authorize and generate a list of emails for those users:
```
select regnum, id, username, name, email, registered_on from registrants r where id not in (select id from athletes); /* Athletes who have never authorized with the freezingsaddles.org site */

select r.regnum, a.id, r.username, r.name, r.email, r.registered_on from registrants r inner join athletes a on (r.id = a.id) where a.team_id is null; /* Athletes that need to re-authorize because we can't read their teams */

select email from registrants where id not in (select id from athletes) union select r.email from registrants r inner join athletes a on (r.id = a.id) where a.team_id is null; /* Emails of users from both of the above groups who need to authorize in Strava */
```
