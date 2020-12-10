#!/usr/bin/env powershell
#
# registrants.ps1
#
# Ingest the CSV from the registration software, 
# and emit a SQL file that recreates the registrants table
#
# WARNING:
# There's no SQL Injection protection in this so 
# please carefully inspect the output before
# running it against the production database!
#
# TODO:
# Yes, this should be re-written in Python.
# Powershell just makes it so easy to do CSV processing without any extras though.

param (
  [Parameter(Mandatory=$true)][string]$csvfile
)
Write-Output "drop table if exists registrants;"
Write-Output "create table registrants (regnum int(11), id int(11), username varchar(255), name varchar(255), email varchar(255), registered_on datetime);"
Write-Output "begin;"
$users = import-csv $csvfile
ForEach ($item in $users) {
    $regnum = $item.("#") 
    $id = $item.("Strava user ID")
    $firstname=$item.("First name")
    $lastname=$item.("Last name")
    $username=$item.("Your user name on the Washington Area Bike Forum")
    $email=$item.("E-mail")
    $datesubmitted=$item.("Date Submitted")
    Write-Output "insert into registrants values($regnum, $id, '$username', '$firstname $lastname', '$email', str_to_date('$datesubmitted',
'%M %e, %Y %h:%S %p'));" 
}
Write-Output "commit;"

