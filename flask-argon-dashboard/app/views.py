# -*- encoding: utf-8 -*-
from flask                  import render_template, request, url_for, redirect, send_from_directory
from werkzeug.exceptions    import HTTPException, NotFound, abort
from flask_api              import status

import os, logging 

from app        import app, db, bc

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
#   serial:     Xbee serial number
#   publicKey:  ECC public key generated on the node
#   signature:  ECC-DSA signature over 'serial,publicKey' 
@app.route('/api/v1/node/register', methods = ['POST'])
def registerNewNode():
    content = request.json 
    return {}, status.HTTP_204_NO_CONTENT
    res = {
        "status": 400,
        "message": "Invalid key or duplicate serial number."
    }
    return res, status.HTTP_400_BAD_REQUEST
    res = {
        "status": 401,
        "message": "Invalid signature."
    }
    return res, status.HTTP_401_UNAUTHORIZED




# expected fields:
#   serial:     Xbee serial number
#   cnonce:     Nonce for the request
#   signature:  ECC-DSA signature over 'serial,cnonce' 
@app.route('/api/v1/node/hello', methods = ['POST'])
def initNode():
    content = request.json 
    res = {
        "status": 200,
        "message": "Handshake successful."
    }
    return res, status.HTTP_200_OK
    res = {
        "status": 400,
        "message": "Invalid nonce."
    }
    return res, status.HTTP_400_BAD_REQUEST
    res = {
        "status": 401,
        "message": "Invalid serial or signature."
    }
    return res, status.HTTP_401_UNAUTHORIZED




# expected fields:
#   serial:     Xbee serial number
#   measurement[n .type]:  Sensor type
#   measurement[n .value]:  Measurement
@app.route('/api/v1/measurement', methods = ['POST'])
def insertMeasurement():
    content = request.json 
    return {}, status.HTTP_204_NO_CONTENT
    res = {
        "status": 400,
        "message": "Invalid sensor type."
    }
    return res, status.HTTP_400_BAD_REQUEST
    res = {
        "status": 401,
        "message": "Invalid serial or signature."
    }
    return res, status.HTTP_401_UNAUTHORIZED