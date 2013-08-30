#!/usr/bin/python
# -*- coding: utf-8 -*-

from queue_manager import QueueManager
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, _app_ctx_stack,jsonify
import json
import re
import logging; logging.basicConfig(filename='css.log', level=logging.NOTSET, format='%(asctime)s - %(levelname)s:%(message)s')
import random

# configuration
DEBUG = False
BossOnHome = 0
BossKey = None
queue = QueueManager()
standardStartVideoId = 'dQw4w9WgXcQ'
standardEndVideoId = 'EHk4B1MtQF8'
SECRET_KEY = str(random.randrange(100000))

# create our little application :)
app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

@app.route('/')
def show_entries():
    global queue
    print queue
    return render_template('list.html',queue=queue)

@app.route('/js')
@app.route('/js/<name>')
def jsfiles(name):
    return render_template('/js/'+name)

@app.route('/login',methods=['GET','POST'])
def login():
    global BossOnHome
    global queue

    print 'BossOnHome: '+ str(BossOnHome)
    if BossOnHome == 0:
        BossOnHome = 1
        session['logged_in'] = True
        logging.info("Usuario logado")
        flash('You were logged in')
        return render_template('list.html',queue=queue)
    return render_template('list.html',queue=queue)

@app.route('/logout',methods=['GET','POST'])
def logout():
    global BossOnHome
    global queue

    if BossOnHome == 1:
        BossOnHome = 0
        session.pop('logged_in',None)
        logging.info('Usuario deslogado')
        return render_template('list.html',queue=queue) 
    return render_template('list.html',queue=queue)

@app.route('/_next',methods=['POST','GET'])
def next():
    global queue
    global standardStartVideoId

    url = queue.next()
    if url is not None:
        match = re.search('.*[w][a][t][c][h].[v][=]([^/]*)',url)
        if match:
            videoId = match.group(1)
        else:
            logging.info('Id não encontrada! '+url)
            videoId = standardStartVideoId
        logging.info('Playing next song: '+videoId)
        return json.dumps(videoId)
    else:
        return json.dumps(standardEndVideoId)

@app.route('/_update',methods=['POST','GET'])
def update():
    global queue

    print queue.getQueue()
    return json.dumps(queue.getQueue())

@app.route('/_clear-all',methods=['POST','GET'])
def clear_all():
    global queue

    logging.info('Clearing queue')
    queue.clear()
    return 'Ok'

@app.route('/_add_url',methods=['POST','GET'])
def add_url():
    global queue

    url = request.args.get('element',0,type=str)
    match = re.search('[h][t][t][p][:][/][/][w][w][w][\.][y][o][u][t][u][b][e][\.][c][o][m][/][w][a][t][c][h][\?][v][\=](.*)',url)
    if match:
        queue.add(url)
        print 'Python says: '+url
        logging.info('Added '+url)
    else:
        print 'Url invalida '+url
        logging.info('Error! URL Invalid '+url)
    return str(len(queue.queue)+1)

@app.route('/_rm_url',methods=['POST','GET'])
def rm_url():
    global queue

    try:
        if session['logged_in'] == True:
            url = request.args.get('element',0,type=str)
            print 'removendo '+str(url)
            logging.info('Removing '+url)
            queue.rm(url)
    except Exception,err:
        logging.info(err)
        logging.info("Usuario sem permissões para remover item")
    return 'Ok'

if __name__ == '__main__':
    app.run(debug=DEBUG,host='0.0.0.0')
    #app.run(debug=False)
