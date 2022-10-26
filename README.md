# FungusDB
Create a weather station inside a Martha using a RaspberryPi

## First Time Database Setup

### Create new user

First connect to default postgres user:

```shell
sudo -u posgres psql
```

Then add first real user:

```postgresql
CREATE USER XXX WITH PASSWORD 'YYY';
```

Create new database:

```postgresql
CREATE DATABASE ZZZ;
```

Add priviledges to user:

```postgresql
GRANT ALL PRIVILEGES ON DATABASE ZZZ TO XXX;
```