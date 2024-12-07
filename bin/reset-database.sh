#!/usr/bin/env bash
# recreate-database.sh
#
# This script is used to recreate the database for the Freezing Model service.
#
# Typically this script is used to reset the database to a clean state for testing.
#
# Usage:
#   APPSETTINGS=test.cfg bin/reset-database.sh
#
#   # or
#
#   MYSQL_ROOT_PASSWORD=your_password MYSQL_DATABASE=your_database SQLALCHEMY_URL=your_url ./recreate-database.sh

set -euo pipefail

APPSETTINGS=${APPSETTINGS:-}

if [[ -n "$APPSETTINGS" ]] && [[ -f "$APPSETTINGS" ]]; then
    # shellcheck disable=SC1090
    source "$APPSETTINGS"
fi

MYSQL_VERSION=${MYSQL_VERSION:-8.0}
MYSQL_HOST=${MYSQL_HOST:-127.0.0.1}
MYSQL_PORT=${MYSQL_PORT:-3306}
MYSQL_USER=${MYSQL_USER:-freezing}
MYSQL_ROOT_USER=${MYSQL_ROOT_USER:-root}
MYSQL_ROOT_PASSWORD=${MYSQL_ROOT_PASSWORD:?You must set a MYSQL_ROOT_PASSWORD environment variable.}
MYSQL_DATABASE=${MYSQL_DATABASE:?You must set a MYSQL_DATABASE environment variable.}
SQLALCHEMY_URL=${SQLALCHEMY_URL:?You must set a SQLALCHEMY_URL environment variable.}

function mysql-freezing-root-non-interactive() {
    docker run -i \
        --rm \
        --network=host \
        mysql:"$MYSQL_VERSION"  \
        mysql \
        --host="$MYSQL_HOST" \
        --port="$MYSQL_PORT" \
        --user="$MYSQL_ROOT_USER" \
        --password="$MYSQL_ROOT_PASSWORD" \
        --default-character-set=utf8mb4
}

mysql-freezing-root-non-interactive <<EOF
drop database if exists $MYSQL_DATABASE;
create database $MYSQL_DATABASE character set utf8mb4;
grant all on freezing_model_test.* to freezing;
EOF
freezing-model-init-db
alembic upgrade head
alembic current
