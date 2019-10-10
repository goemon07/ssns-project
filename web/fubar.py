from flask import Flask
from flask_sqlalchemy import SQLAlchemy 
import os, enum

# Init
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
# Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'fubar.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Init db
db = SQLAlchemy(app)

class sensor_enum(enum.Enum):
    temperature = 0
    humidity = 1
    motionX = 2
    motionY = 3
    motionZ = 4

# Record model
class Measurement(db.Model):
    __tablename__ = 'measurements'
    id = db.Column(db.BigInteger, primary_key=True)
    node_id = db.Column(db.Integer, db.ForeignKey('nodes.id'), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    sensor = db.Column(db.Enum(sensor_enum), nullable=False)
    value = db.Column(db.Float, unique=True, nullable=False)
        
    def __repr__(self):
        return '<Measurement %r>' % self.id

class Node(db.Model):
    __tablename__ = 'nodes'
    id = db.Column(db.Integer, primary_key=True)
    serial = db.Column(db.BigInteger, nullable=False)

    def __repr__(self):
        return '<Node %r>' % self.id


db.create_all()
