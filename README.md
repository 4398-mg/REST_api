-- REST API --
This is the REST API repository for Wimbo, an application that generates music using RNNs.

Features:
- Song generations for Jazz, Folk, Classical, and Game music genres
- Save songs to your history (for logged in users)
- Edit song names
- Delete Songs
- Generate Sheet Music for the generated music

Known bugs:
- There are no known bugs for the REST API

Install and Build:
To install and build the REST API you must first clone this repository (see below for command)
"git clone https://github.com/4398-mg/REST_api"
You must then install the requirements for the project
"pip3 install -r requirements.txt"
From there you should be able to run the REST API through the command
"sudo python3 manage.py gunicorn"

Configuration:
In order to configure the REST API accordingly, you must create a mongoDB instance and an AWS S3 instance. The credentials for these objects will be used in the running of the REST API.

You must first provide the correct mongoDB URL in manage.py.
You must then export environment variables for the database user and database password in order to connect to the database.
Export them as DB_USER and DB_PASS accordingly.

In order to connect to the AWS S3 instance, you must export your AWS ID and AWS Secret ID as environment variables.
Export them as AWS_ID and AWS_SECRET_ID accordingly.
