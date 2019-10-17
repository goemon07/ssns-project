# -*- encoding: utf-8 -*-
from flask                  import render_template, request, url_for, redirect, jsonify, send_from_directory
from werkzeug.exceptions    import HTTPException, NotFound, abort
from flask_api              import status

import os, logging 

from app                import app, db, bc
from app.models         import Node, Measurement
from flask_sqlalchemy   import SQLAlchemy, inspect
from datetime           import datetime

@app.route('/sitemap.xml')
def sitemap():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'sitemap.xml')

@app.route('/googlee35aa2f2fd7b0c5b.html')
def google():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'googlee35aa2f2fd7b0c5b.html')

@app.route('/print')
def printMsg():
    app.logger.warning('testing warning log')
    app.logger.error('testing error log')
    app.logger.info('testing info log')
    return "Check your console"

# Render the icons page
@app.route('/icons.html')
def icons():

    return render_template('layouts/default.html',
                            content=render_template( 'pages/icons.html') )

# Render the tables page
@app.route('/tables.html')
def tables():

    return render_template('layouts/default.html',
                            content=render_template( 'pages/tables.html') )

# App main route + generic routing
@app.route('/', defaults={'path': 'index.html'})
@app.route('/<path>')
def index(path):

    content = None

    try:

        # try to match the pages defined in -> pages/<input file>
        return render_template('layouts/default.html',
                                content=render_template( 'pages/'+path) )
    except:
        
        return render_template('layouts/auth-default.html',
                                content=render_template( 'pages/404.html' ) )


#####################################################
####################### API #########################
#####################################################

# expected fields:
#   serial:     Xbee serial number in HEX
@app.route('/api/v1/node/register', methods = ['POST'])
def register_new_node():
    content = request.json 
    try:
        new_node = Node(serial=content['serial'])
        db.session.add(new_node)
        db.session.commit()
        return {}, status.HTTP_204_NO_CONTENT
    except Exception as e:
        print(e)
        res = {
            "status": 400,
            "message": "Invalid key or duplicate serial number."
        }
        return res, status.HTTP_400_BAD_REQUEST



# expected fields:
#   serial:     Xbee serial number
#   type:  Sensor type
#   value:  Measurement
@app.route('/api/v1/measurement', methods = ['POST'])
def insert_measurement():
    try:
        content = request.json
        new_meas = Measurement(node_serial=content['serial'], timestamp=datetime.now(), sensor=content['type'], value=content['value'])
        db.session.add(new_meas)
        db.session.commit()
        return {}, status.HTTP_204_NO_CONTENT
    except Exception as e:
        print(e)
        res = {
            "status": 400,
            "message": "Invalid sensor type or not existing sensor serial."
        }
        return res, status.HTTP_400_BAD_REQUEST

def object_as_dict(obj):
    return {c.key: getattr(obj, c.key)
            for c in inspect(obj).mapper.column_attrs}

# expected fields:
#   token:  Token used for paging (measurement id, uint8)
@app.route('/api/v1/measurement', methods = ['GET'])
def read_measurements():
    try:
        res = Measurement.query.all()
        res_list = []
        token = 0
        for mes in res:
            if mes.id > token:
                token = mes.id    
            res_list.append(object_as_dict(mes))
        res_list.append({'token': token})
        return jsonify(res_list), status.HTTP_200_OK
    except Exception as e:
        print(e)
        res = {
            "status": 500,
            "message": "Internal server error."
        }
        return res, status.HTTP_500_INTERNAL_SERVER_ERROR