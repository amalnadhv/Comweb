#!/usr/bin/env bash
set -e

echo "==== Installing MS SQL ODBC Driver ===="

curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
curl https://packages.microsoft.com/config/ubuntu/22.04/prod.list \
    > /etc/apt/sources.list.d/mssql-release.list

apt-get update -y
ACCEPT_EULA=Y apt-get install -y msodbcsql18 unixodbc unixodbc-dev
