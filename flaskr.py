# -*- coding: utf-8 -*-
"""
    Flaskr
    ~~~~~~

    A microblog example application written as Flask tutorial with
    Flask and sqlite3.

    :copyright: (c) 2010 by Armin Ronacher.
    :license: BSD, see LICENSE for more details.
"""

from queue_manager import QueueManager
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, _app_ctx_stack,jsonify
import json

# configuration
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

# create our little application :)
app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

queue = QueueManager()


@app.route('/')
def show_entries():
    print queue
    return render_template('list.html',queue=queue)

@app.route('/js')
@app.route('/js/<name>')
def jsfiles(name):
    return render_template('/js/'+name)

@app.route('/_next',methods=['POST','GET'])
def next():
    return json.dumps(queue.next())

@app.route('/_update',methods=['POST','GET'])
def update():
    print queue.getQueue()
    return json.dumps(queue.getQueue())

@app.route('/_clear-all',methods=['POST','GET'])
def clear_all():
    queue.clear()
    return 'Ok'

@app.route('/_add_url',methods=['POST','GET'])
def add_url():
    url = request.args.get('element',0,type=str)
    queue.add(url)
    print 'Python says: '+url
    return str(len(queue.queue)+1)

@app.route('/_rm_url',methods=['POST','GET'])
def rm_url():
    url = request.args.get('element',0,type=str)
    print 'removendo '+str(url)
    queue.rm(url)
    return 'Ok'

if __name__ == '__main__':
    app.run()
