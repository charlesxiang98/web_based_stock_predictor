import os
from multiprocessing import Pool, cpu_count

from flask import Flask
# from werkzeug.contrib.fixers import ProxyFix
from pymongo import MongoClient

pool = Pool(cpu_count())


app = Flask(__name__)

# app.wsgi_app = ProxyFix(app.wsgi_app)


# app.config.from_pyfile('config.py')


client = MongoClient(host='localhost', port=27017)
daily = client['stockapp']['daily']
realtime = client['stockapp']['realtime']
comment = client['stockapp']['comment']

from .views import *
from .view_emergency import *
