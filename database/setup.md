# How to Install and Set up the Database

Some general tips to keep in mind:

1. Commands issued after `sudo su postgres` do not need extra sudo rights.
2. You may need to change directory permissions.
3. Check if the hard drive is correctly partitioned.
4. Keep calm.

## Installation

We first install all packages that are necessary for postgres:
```bash
sudo apt-get install postgresql libpq-dev postgresql-client postgresql-client-common pgadmin3
```

## Configure to Use the External Hard Drive

The SD-card of our Raspberry is rather small.
Thus, we do not want to write all our data to it.
Instead, we want to hook up an external hard drive.

### Step 1: Create a Mount Point

The first step is to mount the hard drive.
Therefore, we need to first create a directory that serves as our mount point.
For example this can live in the `/media` directory of your filesystem.
If you put it anywhere else, you may need to change the permissions for it.

```bash
sudo mkdir -p __your_mount_point__
```

### Step 2: Configure Automatic Mounting of Hard Drive

First we need to find the UUID and the file system type of the hard drive. The command

```bash
lsblk -o NAME,FSTYPE,UUID,MOUNTPOINT
```

gives us both.
Next we need to configure the `fstab` file.

```bash
sudo nano /etc/fstab
```

and add the line

```
< file system >     <  mount point >      < file system type>   < options >     < dumpp >  < pass >
UUID=__your_UUID__  __your_mount_point__  __file_system_type__  defaults         0         0
```

and don't forget to test your `fstab` configuration. 
A broken `fstab` can render your disk un-bootable.
Now reboot.

### Step 3: Setup Postgres

Install postgreSQL:

```bash
sudo apt install postgresql libpq-dev postgresql-client postgresql-client-common -y
```

In order to write to the hard drive, we need to change the configuration file.

```bash
sudo systemctl stop postgresql
sudo nano /etc/postgresql/13/main/postgresql.conf
```

Edit the `data_directory` to point to the mounted Hard Drive on `__your_mount_point__` 

### Step 4: Initialize a new Database on the Hard Drive 

The steps below are a standard approach. 
The steps will vary according to specific requirements, and may require a more customised approach

We need to create a blank directory on the target path: 

```bash
mkdir /__your_mount_point__/__data_dir__
```

and change ownership to the postgres user, for example

```bash
chown  postgres:postgres /__your_mount_point__/__data_dir__
```
next we use the `initdb` program to create a new PostgreSQL database cluster at our desired location.

```bash
sudo su postgres
/usr/lib/postgresql/13/bin/initdb -D /__your_mount_point__/__data_dir__
systemctl start postgresql@13-main
```

Note that the path to `initdb` can vary!
If you are not sure how to call your `initdb`, you can find out by running 
```bash
sudo find -name initdb`
```

### Step 5: Create Databases

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

and - optionally - connect to the `dev` database:

```psql
\connect dev
```

### Step 6: Enable postgres Server on Startup

Finally, we want postgres to run whenever the server starts: 

```bash
sudo update-rc.d postgresql enable
sudo systemctl enable postgresql
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

