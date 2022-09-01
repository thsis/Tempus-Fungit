#!/usr/bin/env sh
echo 'installing required os-packages...'
sudo apt-get install build-essential python-dev python-openssl
echo 'done.'

echo 'installing required python packages...'
pip install -r requirements.txt
pip install -e .
echo 'done.'