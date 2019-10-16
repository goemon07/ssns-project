# -*- encoding: utf-8 -*-
import os

from flask            import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt     import Bcrypt

from flask_restful     import Api

# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

api = Api(app) # flask_restful

app.config.from_object('app.configuration.Config')

db = SQLAlchemy  (app) # flask-sqlalchemy
bc = Bcrypt      (app) # flask-bcrypt

from app import views
from app.restapi.stats import ApiStats 

# Inject REST api 
api.add_resource(ApiStats, '/api/stats/<string:segment>')

