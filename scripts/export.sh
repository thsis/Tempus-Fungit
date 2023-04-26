#!/usr/bin/env bash

echo Enter user:
read user
echo Enter host:
read host

scp $user@$host:FungusDB/data/*.csv data
scp $user@$host:FungusDB/logs/*.log logs