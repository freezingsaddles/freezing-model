#!/usr/bin/env python3
"""
This script reads a CSV file of registrants from https://freezingsaddles.info and outputs SQL commands to create a table and insert the registrants into the table.

Auto-generated from registrants.ps1 by GitHub Copilot.
Author: @obscurerichard
Usage: python registrants.py <csvfile>
"""
import csv
import sys
from datetime import datetime

from pymysql.converters import escape_string


def main(csvfile):
    print("drop table if exists registrants;")
    print(
        "create table registrants (regnum int(11), id int(11), username varchar(255), name varchar(255), email varchar(255), registered_on datetime);"
    )
    print("begin;")

    with open(csvfile, newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            regnum = int(row["#"])
            id = int(row["Strava user ID"])
            firstname = escape_string(row["First Name"])
            lastname = escape_string(row["Last Name"])
            username = escape_string(
                row["Your user name on the Washington Area Bike Forum"]
            )
            email = escape_string(row["E-mail"])
            datesubmitted = datetime.strptime(
                row["Date Submitted"], "%B %d, %Y %I:%M %p"
            )
            datesubmitted_str = datesubmitted.strftime("%Y-%m-%d %H:%M:%S")
            print(
                f"insert into registrants values({regnum}, {id}, '{username}', '{firstname} {lastname}', '{email}', '{datesubmitted_str}');"
            )
    print("commit;")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python registrants.py <csvfile>")
        sys.exit(1)
    main(sys.argv[1])
