'''
    manage.py

    Server start module
'''

import os
from app import create_app
from flask_script import Manager, Shell, Command, Option
from pymongo import MongoClient
from flask_cors import CORS
import boto
import boto.s3
import sys


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


app = create_app(os.getenv('FLASK_CONFIG') or 'default')
app.debug = True

CORS(app)

manager = Manager(app)


def read_env_vars(filename='/home/ubuntu/REST_api/env_vars.txt'):
    try:
        with open(filename, 'r') as f:
            for line in f.readlines():
                key, value = line.split()
                app.config[key] = value
    except Exception as e:
        print(bcolors.WARNING + "unable to read env_vars from file: " +
              filename + bcolors.ENDC)


read_env_vars()

try:
    conn = boto.connect_s3(
        app.config['AWS_ID'], app.config['AWS_SECRET_ID'], is_secure=False)
    print(bcolors.OKGREEN+"Connected to S3 instance"+bcolors.ENDC)
except:
    print(bcolors.FAIL+"Failed to connect to S3 instance"+bcolors.ENDC)
    sys.exit(0)
try:
    bucket = conn.get_bucket('wimbo-music-bucket')
    print(bcolors.OKGREEN+"Connected to bucket"+bcolors.ENDC)
except:
    print(bcolors.FAIL+"Failed to connect to bucket"+bcolors.ENDC)
    bucket = conn.create_bucket('wimbo-music-bucket')

# for mongodb use
mongo_url = ('mongodb://%s:%s@ds131905.mlab.com'
             ':31905/music_gen' % (app.config['DB_USER'],
                                   app.config['DB_PASS']))

print(bcolors.OKBLUE + mongo_url + bcolors.ENDC)
client = MongoClient(mongo_url, connect=False)
try:
    client.server_info()
    print(bcolors.OKGREEN+"Connected to database"+bcolors.ENDC)
except Exception as e:
    print(bcolors.FAIL+"Unable to connect to database"+bcolors.ENDC)


def make_shell_context():
    return dict(app=app)


@manager.option('-h', '--host', dest='host', default='0.0.0.0')
@manager.option('-p', '--port', dest='port', type=int, default=1337)
@manager.option('-w', '--workers', dest='workers', type=int, default=4)
def gunicorn(host, port, workers):
    """Start the Server with Gunicorn"""
    from gunicorn.app.base import Application

    class FlaskApplication(Application):
        def init(self, parser, opts, args):
            return {
                'bind': '{0}:{1}'.format(host, port),
                'workers': app.config['WORKER_POOL_SIZE'],
                'timeout': 120
            }

        def load(self):
            return app

    application = FlaskApplication()
    return application.run()


manager.add_command("shell", Shell(make_context=make_shell_context))

if __name__ == '__main__':
    manager.run()
