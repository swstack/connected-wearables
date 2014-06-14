Connected Wearables
===================

The connected wearables project was created for an Etherios hackathon
in order to connect data from wearable devices to the Device Cloud by
Etherios.  The project was created by 3 endingeers from Etherios
Wireless Design Servies: Paul Osborne
([posborne](https://github.com/posborne)),
Tom Manley ([tpmanley](https://github.com/tpmanley)), and Stephen
Stack
([swstack](https://github.com/swstack)).


System Architecture
===================

High Level
----------

The basic architecture for the connected wearables system is pretty
simple overall as shown in this architecture diagram.

![Architecture
 Diagram](https://raw.githubusercontent.com/swstack/connected-wearables/master/cwear-archdiagram.png)

Notable things from the overall architecture:

* System consists of two processes.  One is just responsible for doing
  web interface things and the other runs in the background and
  synchronizes data between the device cloud and humanapi.
* The two applications share state via a PostgreSQL database with a
  few simple relations.  Data from humanapi is not stored in this
  database.
* The web interface allows for configuration of multiple
  "applications" so that synchronization can happen between multiple
  humanapi and device cloud accounts.
* Great care is taken to perform the humanapi -> device cloud
  synchronization with great efficiency.  During the poll period for
  each logical application, the human api is polled for changes to
  data for all associated users since the last time we checked -- in
  turn, those changes are batched in web service calls of up to 250
  datapoints and are written to streams on the device cloud.


Implementation Highlights
-------------------------

### Cloud Streams Design

Choosing a proper path for data streams based on the data being
received from the HumanAPI was a challenge.  As there did not seem to
be one-size-fits-all
solution for all potential consumers of data out of the device cloud,
we attempted to provide
a fwe options to that implementor.

For all cases, the following basic stream path format is used:

```
/human/<userid>/<endpoint>/<field/key>
```

An example which would include the "steps" for a user over time being:

```
human/537ac6902f143657390c766e/activities/steps
```

### Mapping from HumanAPI -> Device Cloud Streams

The actual mapping of data from the humanapi data sources to streams
in the device cloud
is done in an elegant and streamlined fashion.  Rather than having
loads of code for each
endpoint (e.g. activities, blood_glucose, etc.) a generic way to
describe the form of
the data from HumanAPI and those parts that we want to map to the
Device Cloud is used.

This mapping can be found in
[humanapi_mapping.yml](https://github.com/swstack/connected-wearables/blob/master/src/cwear/bridge/humanapi_mapping.yml)

An exmaple of how the mapping is done for blood_oxygen information is
shown here:

```
# Property	Type	Description
# -----------------------------
# id	    String	The id of the blood oxygen measurement
# userId    String	The global Id of the user
# timestamp Date	The original date and time of the measurement
# source    String	The source service for the measurement, where
it was created
# value	    Number	The value of the measurement in the unit
specified
# unit	    String	The unit of the measurement value
# createdAt Date	The time the measurement was created on the
Human API server
# updatedAt	Date	The time the measurement was updated on the
Human API server
blood_oxygens:
  timestamp_field: timestamp
  forward_fields:
    source: string
    value:
      type: float
      unit_field: unit
    createdAt: datetime
    updatedAt: datetime
```

Based on this, we know to do things like take the "value" field from
humanapi data
received on this endpoint and send it along to the device cloud with
the stream
unit for that stream set to be the "unit" field from the JSON document
received
from humanapi.  This makes changing what gets sent extremely simple.


Developer's Guide
=================

The connected wearables is written for Python 2.7 and is designed to
run on Heroku.

System Dependencies
-------------------

* Python 2.7
* Pip
* Virtualenv
* PostgreSQL

Install these for your sytem.  To setup a virtualenv and install
dependencies for
development you can do the following:

```sh
$ virtualenv env
$ source env/bin/activate
(env) $ pip install -r requirements.txt
```


Development Database Setup
--------------------------

Although it is possible to tell SQLAlchemy to use sqlite during
development, we
find it preferrable to install postgresql to minimize difference
between production
and development platforms.

Create a postgresql user and database:

```sh
postgres=# create user cwear password 'cwear';
postgres=# create database cwear owner cwear;
```

Run the latest migrations:

```sh
$ alembic upgrade head
```

Deploying to Production
-----------------------

As mentioned, heroku is used for deployment.  Follow the basic
instructions online
and things should mostly just work.

If a new version includes changes to the database (captured in an
alembic migration)
then you will need to run the following to ensure that the migraton
happens on the
production database.

```sh
$ heroku run alembic upgrade head
```
