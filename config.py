'''
    config.py
    Configuration module for the server
'''

import os
basedir = os.path.abspath(os.path.dirname(__file__))

from uuid import uuid5, NAMESPACE_DNS
from socket import gethostname


class Config:
    def __init__(self):
        pass
    VERSION = "1.0"
    AUTHOR = "Jake Lawrence"
    NAME = ""

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    LOGLEVEL = DEBUG
    DB_USER = os.getenv('DB_USER')
    DB_PASS = os.getenv('DB_PASS')
    WORKER_POOL_SIZE = 4
    AWS_ID = os.getenv('AWS_ID')
    AWS_SECRET_ID = os.getenv('AWS_SECRET_ID')


class ProductionConfig(Config):
    DEBUG = False
    LOGLEVEL = ''
    DB_USER = os.getenv('DB_USER')
    DB_PASS = os.getenv('DB_PASS')
    WORKER_POOL_SIZE = 4
    AWS_ID = os.getenv('AWS_ID')
    AWS_SECRET_ID = os.getenv('AWS_SECRET_ID')

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': ProductionConfig
}
