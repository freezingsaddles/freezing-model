#!/usr/bin/env powershell
param (
  [Parameter(Mandatory=$true)][string]$csvfile
)
# Yes, this should be re-written in Python.
# Powershell just makes it so easy to do CSV processing without any extras though.
Write-Output "drop table if exists registrants;"
Write-Output "create table registrants (id int(11), username varchar(255), firstname varchar(255), lastname varchar(255), registered_on datetime);"
Write-Output "begin;"
$users = import-csv $csvfile
ForEach ($item in $users) { 
    $id = $item.("Strava user ID")
    $firstname=$item.("First name")
    $lastname=$item.("Last name")
    $username=$item.("Your user name on the Washington Area Bike Forum")
    $datesubmitted=$item.("Date Submitted")
    Write-Output "insert into registrants values($id, '$username', '$firstname', '$lastname', 	str_to_date('$datesubmitted',
'%M %e, %Y %h:%S %p'));" 
}
Write-Output "commit;"

