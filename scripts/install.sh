#!/usr/bin/env sh
echo 'installing required os-packages...'
sudo apt-get install build-essential python-dev python-openssl posgresql libatlas-base-dev libgpiod-dev python3-tk libpq-dev postgresql-client postgresql-client-common pgadmin3
echo 'done.'

echo 'installing required python packages...'
pip install -r requirements.txt
pip install -e .
echo 'done.'

echo 'creating folder for the database...'
mkdir -pv ~/Tempus-Fungit-DB
echo 'done.'