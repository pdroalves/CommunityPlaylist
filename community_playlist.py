#!/usr/bin/python
# -*- coding: utf-8 -*-
	
##    This file is part of Community Playlist.
##
##    Community Playlist is free software: you can redistribute it and/or modify
##    it under the terms of the GNU General Public License as published by
##    the Free Software Foundation at version 3.

##
##    Community Playlist is distributed in the hope that it will be useful,
##    but WITHOUT ANY WARRANTY; without even the implied warranty of
##    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##    GNU General Public License for more details.
##
##    You should have received a copy of the GNU General Public License
##    along with Community Playlist.  If not, see <http:##www.gnu.org/licenses/>

##    Author: 
#	Pedro Alves, pdroalves@gmail.com
#		28 August, 2013 - Campinas,SP - Brazil


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
song_playing = None
now_playing = False

standardStartVideoId = 'dQw4w9WgXcQ'
standardEndVideoId = 'F0BfcdPKw8E'
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
        #return render_template('list.html',queue=queue,key=SECRET_KEY)
    return render_template('list.html',queue=queue)

@app.route('/logout',methods=['GET','POST'])
def logout():
    global BossOnHome
    global queue
    global now_playing
    global SECRET_KEY

    #print request
    #key = request.args.get('key',0,type=str)
    #if session['logged_in']:
    BossOnHome = 0
    now_playing = 0
    session.pop('logged_in',None)
    logging.info('Usuario deslogado')
    #SECRET_KEY = str(random.randrange(100000))
    return render_template('list.html',queue=queue)

@app.route('/_next',methods=['POST','GET'])
def next():
    global queue
    global standardStartVideoId

    videoId = queue.next()
    if videoId is not None:
        logging.info('Playing next song: '+videoId)
        return json.dumps(videoId)
    else:
        return json.dumps(standardEndVideoId)

@app.route('/_set_playing',methods=['GET'])
def set_playing():
    global now_playing
    global song_playing

    now_playing = request.args.get('now_playing',0,type=int)
    song_playing = request.args.get('song_playing',0,type=str)

    return 'Ok'

@app.route('/_get_playing',methods=['GET'])
def get_playing():
    global now_playing
    global song_playing

    status = dict(
            now_playing=now_playing,
            song_playing=song_playing
             )

    return json.dumps(status)


@app.route('/_update',methods=['POST','GET'])
def update():
    global queue

    if DEBUG:
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
    match = re.search('.*[w][a][t][c][h].[v][=]([^/,&]*)',url)
    if match:
        queue.add(match.group(1))
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
            if DEBUG:
                print 'removendo '+str(url)
            logging.info('Removing '+url)
            queue.rm(url)
    except Exception,err:
        logging.info(err)
        logging.info("Usuario sem permissões para remover item")
    return 'Ok'

@app.route('/blablablaNewBoss',methods=['POST','GET'])
def clear_boss():
    return logout()

if __name__ == '__main__':
    #app.run(debug=DEBUG,host='0.0.0.0')
    app.run(debug=True)
