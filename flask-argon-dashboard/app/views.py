# -*- encoding: utf-8 -*-
from flask               import render_template, request, url_for, redirect, send_from_directory
from werkzeug.exceptions import HTTPException, NotFound, abort

import os, logging 

from app        import app, lm, db, bc

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
