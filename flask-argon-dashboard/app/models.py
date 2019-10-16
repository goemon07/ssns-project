# -*- encoding: utf-8 -*-
from app import db

    # 0 = temperature 
    # 1 = humidity    
    # 2 = motionX     
    # 3 = motionY     
    # 4 = motionZ     

# Record model

class Node(db.Model):
    __tablename__ = 'nodes'
    id = db.Column(db.Integer, primary_key=True)
    serial = db.Column(db.String, nullable=False, unique=True)

    def __repr__(self):
        return '<Node %r>' % self.id


class Measurement(db.Model):
    __tablename__ = 'measurements'
    # variant needed for the autoincrement since bigint in sqlite are not autoinc by default 
    id = db.Column(db.BigInteger().with_variant(db.Integer, "sqlite"), primary_key=True)
    node_serial = db.Column(db.String, db.ForeignKey('nodes.serial'), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    sensor = db.Column(db.Integer, nullable=False)
    value = db.Column(db.Float, nullable=False)
        
    def __repr__(self):
        return '<Measurement %r>' % self.id