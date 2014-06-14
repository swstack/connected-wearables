Etherios Hackathon - Connected Wearables
===================

System Dependencies
-------------------

* PostgreSQL

```sh
$ sudo apt-get install postgresql
```

Development Database Setup
--------------------------

Create a user and database:
```sh
postgres=# create user cwear password 'cwear';
postgres=# create database cwear owner cwear;
```

Run the latest migrations:
```sh
$ alembic upgrade head
```