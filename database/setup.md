# How to Install and Set up the Database

## Installation
```bash
sudo apt-get install postgresql libpq-dev postgresql-client postgresql-client-common pgadmin3
```

## Configure to Use the External Hard Drive


```bash
sudo mkdir -p /mnt/HDD
sudo mount /dev/sda /mnt/HDD
sudo nano etc/postgresql/13/main/postgresql.conf
```

Prepare a directory to mount the external hard drive to.
Mount the hard drive to `/mnt/HDD`
Edit the `data_directory` to point to the mounted Hard Drive on `/mnt/HDD` 

## Create Database

Initial setup for the first user:

```bash
sudo su postgres
createuser __your_user__ -P --interactive
```

Create another database, from the current `postgres` user whose name is the same as the user you created.
We do this in order to have a more convenient access to the CĹI.

```bash
psql
create database __your_user__;
```

Create the final databases

```psql
create database dev;
create database prod;
```

and connect to the `dev` database:

```psql
connect \dev
```

## Create Tables for Raw Data

Set up the first tables for the raw data.
```make tables```

### Raw Recipes Table

Table for any recipes. This table takes its data from `recipes/recipes.csv` 

### Raw Sensor Data Table

Table that collects the raw sensor output. This table takes its data from `data/sensor_output.csv`

### Raw Experiment and Observation Table

Table that collects the data obtained from setting up and observing the results of the experiments.
At the moment this data is ingested through a Google Sheets spreadsheet.

### Raw Yield Table

Table that collects the outcome of each experiment

