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

import os
import json
import re
import binascii
import string
import sqlite3
import logging; logging.basicConfig(filename='css.log', level=logging.NOTSET, format='%(asctime)s - %(name)s - %(levelname)s:%(message)s')
from time import time
from queue_manager import QueueManager
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, _app_ctx_stack,jsonify
from youtube_handler import YoutubeHandler

# configuration
title = "Community Playlist"
DEBUG = True
BossOnHome = 0
LastBossCall = 0
MaxCallInterval = 21
song_playing = None
now_playing = False
current_time = 0
song_id = ''
default_key = 'chave'

standardStartVideoId = 'dQw4w9WgXcQ'
standardEndVideoId = 'F0BfcdPKw8E'
privileges_map = {
"boss":101,
"nil":100
}
permissions = {
    "set_playing":[privileges_map.get('boss')],
    "next":[privileges_map.get('boss')],
    "clear-all":[privileges_map.get('boss')],
    "add":[privileges_map.get('boss')],
    "rm":[privileges_map.get('boss')]
}

app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

queue = QueueManager()
yth = YoutubeHandler()

logger = logging.getLogger("Main")

class LoginGatekeeper:
    def __init__(self,path="database.db"):
        self.logger = logging.getLogger('DB')
        self.path = path
        self.create_database()

        ## Each operation should happen in a transaction
        # and should create a new connection
    def __connect(self):
        self.db = sqlite3.connect(self.path)
        if self.db is None:
            raise Exception("Couldn't create database")
        else:
            self.logger.info("Database connection UP")

    def __close(self):
        if self.db is not None:
            self.db.commit()
            self.db.close()
            self.logger.info("Database connection DOWN")

    def __query(self,q):
        if self.db is not None:
            return self.db.execute(q)
        else:
            raise Exception("Connection to database is closed")

    def create_database(self):
        # To-do
        # This database must be encrypted
        try:
            self.__connect()
            self.__query("CREATE TABLE IF NOT EXISTS user (id INTEGER PRIMARY KEY,name TEXT,username TEXT UNIQUE,password TEXT,privileges INTEGER,removed INTEGER)")
            self.__query("CREATE TABLE IF NOT EXISTS session (id INTEGER PRIMARY KEY,fk_user INTEGER,created_ts INTEGER,key TEXT)")     
            self.__query("INSERT OR IGNORE INTO user (username,password,privileges) VALUES ('admin','admin',"+str(privileges_map.get("boss"))+")")       
        finally:
            self.__close()
        return

    def add_user(self,user):
        # To-do
        # Add a new user
        try:
            self.__connect()
        finally:
            self.__close()

    def get_user(self,credentials=None,session=None):
        # Try to find a user with that session key
        data = None
        try:
            self.__connect()
            if credentials is not None:
                cursor = self.__query("SELECT name,privileges,id FROM user WHERE username = \""+credentials.get('username')+"\" AND password = \""+self.encrypt(credentials.get('password'))+"\" limit 1")
                data = [dict(name=row[0],privileges=row[1],id=row[2]) for row in cursor.fetchall()]
            else:
                cursor = self.__query("SELECT name,privileges,user.id FROM user INNER JOIN session ON user.id = session.fk_user WHERE key = \'"+session+"\' limit 1")
                data = [dict(name=row[0],privileges=row[1],id=row[2]) for row in cursor.fetchall()]
        finally:
            self.__close()

        return data

    def check_user_keys(self,user,keys):
        # To-do
        # Check if a key provided matchs the user key        
        try:
            self.__connect()
        finally:
            self.__close()

    def get_user_session(self):
        # To-do
        # Get the logged session    
        try:
            self.__connect()
        finally:
            self.__close()        

    def set_user_session(self,data):
        # Set the logged session
        try:
            self.__connect()
            if data is not None:
                ts = int(time())
                self.__query("INSERT INTO session (fk_user,created_ts,key) VALUES(\""+str(data.get("fk_user"))+"\","+str(ts)+",\""+data.get("key")+"\")")
        finally:
            self.__close()


    def encrypt(self,txt):
        # To-do
        return txt


def gen_random_key():
    return binascii.hexlify(os.urandom(24))

def get_app_secret_key(path="blue.json"):
    global default_key
    try:
        with open(path) as f:
            data = json.load(f)
            if data.has_key('key'):
                return data.get('key')
            else:
                logger.info("Couldn't get key from "+path+".\nusing default key.")
                return default_key
    except IOError:
        logger.info("Couldn't open "+path+".\nUsing default key.")
        return default_key
      
@app.context_processor
def utility_processor():
    def inject_title():
        global title
        return title

    return dict(
            title=inject_title
            )

@app.route('/')
def show_entries():
    return render_template('index2.html')

@app.route('/js')
@app.route('/js/<name>')
def jsfiles(name):
    return render_template('/js/'+name)


@app.route('/player',methods=['GET','POST'])
def player():
    return render_template('player.html')

@app.route('/login',methods=['GET','POST'])
def login():
    global BossOnHome
    global queue

    try:
        lgk = LoginGatekeeper()
        ## Try to log in by the session key
        if request.form['username'] is None:
            if session.has_key('session_key'):
                print session.get('session_key')
                user_data = lgk.get_user(session=session['session_key'])
                if user_data is None:
                    
                    session.pop('session_key',None)
                    session.pop('boss',None)
                else:                        
                    session['session_key'] = session.get('session_key')
                    session['boss'] = user_data.get('privileges') == privileges_map.get('boss')
        else:
            # Try to log in by normal username/password keys
            user_credentials = {
                "username":request.form['username'],
                "password":lgk.encrypt(request.form['password'])
                }      
            print user_credentials
            user_data = lgk.get_user(credentials=user_credentials)
            if len(user_data) > 0 :
                ## Try to log in user by the credentials provided
                session_key = gen_random_key()
                session['session_key'] = session_key
                print session['session_key']
                #session['boss'] = user_data.get('privileges') == privileges_map.get('boss')
                lgk.set_user_session({"fk_user":user_data[0].get('id'),"key":session_key})
                logger.critical("Usuario logado "+user_credentials.get('username'))
            else:
                raise Exception("No login data found...")
    except Exception,err:
        msg = "Erro ao logar: " + str(err)
        print msg
        logger.critical(msg)
        
        session.pop('session_key',None)

    return render_template('index2.html')

@app.route('/logout',methods=['GET','POST'])
def logout():
    global queue
    global now_playing

    try:        
        session.pop('session_key',None)
        now_playing = -1
        logger.critical('Usuario deslogado')
    except Exception,err:
        print "Erro ao deslogar"
        logger.critical("Erro ao deslogar: "+str(err))

    return render_template('index2.html')

@app.route('/_next',methods=['POST','GET'])
def next():
    global queue
    global standardStartVideoId

    lgk = LoginGatekeeper()

    try:
        if session.has_key('session_key'):
            user = lgk.get_user(session=session['session_key'])[0]
        if user is None:
            raise Exception("No sufficient privileges for this operation.")
        if user.get('privileges') in permissions.get('next'):
            video_url = queue.next()
            if video_url is not None:
                logger.critical('Playing next song: '+video_url)
                return json.dumps(video_url)
            else:
                return json.dumps(standardEndVideoId)
        else:
            raise Exception("No sufficient privileges for this operation.")
            return logout()
    except Exception,err:
        logger.critical(err)
        logger.critical("Usuario sem permissões para tocar videos")
        
        session.pop('session_key',None)
        return render_template('index2.html')
    return 'Ok'

@app.route('/_set_playing',methods=['GET','POST'])
def set_playing():
    global now_playing
    global song_playing
    global current_time
    global song_id
    
    lgk = LoginGatekeeper()

    try:
        user = None
        if session.has_key('session_key'):
            user = lgk.get_user(session=session['session_key'])[0]
        if user is None:
            raise Exception("User not logged...")
        if user.get('privileges') in permissions.get('set_playing'):
            now_playing = request.args.get('now_playing',0,type=int)
            song_playing = request.args.get('song_playing',0,type=str)
            current_time = request.args.get('current_time',0,type=float)
            song_id = request.args.get('song_id',0,type=str)

            if now_playing == 1:
                queue.set_pause(False)
            elif now_playing == 2:
                queue.set_pause(True)

            logger.info('Set Playing: '+'('+song_id+') -'+str(song_playing)+" - "+str(now_playing)+" - "+str(current_time))
        else:
            raise Exception("No sufficient privileges for this operation.")
            return logout()
    except Exception,err:
        logger.critical(err)
        logger.critical("Usuario sem permissões para setar o now playing")
        
        session.pop('session_key',None)
        return render_template('index2.html')
    return 'Ok'

@app.route('/_get_playing',methods=['GET'])
def get_playing():
    global now_playing
    global song_playing
    global current_time
    global song_id

    status = dict(
            title='',
            now_playing=now_playing,
            song_id=song_id,
            song_playing=song_playing,
            current_time=current_time
             )
    logger.info("Now playing: "+str(song_playing))
    return json.dumps(status)


@app.route('/_update',methods=['POST','GET'])
def update():
    global queue
    queue.sort()
    return json.dumps({"queue":queue.getQueue()})

@app.route('/_clear-all',methods=['POST','GET'])
def clear_all():
    global queue
    lgk = LoginGatekeeper()
    
    try:
        user = None
        if session.has_key('session_key'):
            user = lgk.get_user(session=session['session_key'])[0]
        if user is None:
            raise Exception("No sufficient privileges for this operation.")
        if user.get('privileges') in permissions.get('clear-all'):
            logger.critical('Clearing queue')
            queue.clear()
        else:
            raise Exception("No sufficient privileges for this operation.")
            return logout()
    except Exception,err:
        logger.critical(err)
        logger.critical("Usuario sem permissões para setar o now playing")
        
        session.pop('session_key',None)
    return render_template('index2.html')

@app.route('/_add_url',methods=['POST','GET'])
def add_url():
    global queue
    url = request.args.get('element',0,type=str)
    match = re.search('.*[w][a][t][c][h].[v][=]([^/,&]*)',url)
    if match:
        queue.add(url=match.group(1),creator=request.remote_addr)
        print 'Added: '+url
        logger.critical('Added '+url)
    else:
        print 'Invalid url '+url
        logger.critical('Error! URL Invalid '+url)
        
    return str(len(queue.queue)+1)

@app.route('/_rm_url',methods=['POST','GET'])
def rm_url():
    global queue
    lgk = LoginGatekeeper()

    try:
        user = None
        if session.has_key('session_key'):
            user = lgk.get_user(session=session['session_key'])[0]
        if user is None:
            raise Exception("No sufficient privileges for this operation.")
        if user.get('privileges') in permissions.get('add'):
            url = request.args.get('element',0,type=str)
            if DEBUG:
                print 'removendo '+str(url)
            logger.critical('Removing '+url)
            queue.rm(url)
        else:
            raise Exception("No sufficient privileges for this operation.")
            return logout()
    except Exception,err:
        logger.critical(err)
        logger.critical("Usuario sem permissões para remover item")
        session.pop('key',None)
        return render_template('index2.html')
    return 'Ok'

@app.route("/_vote",methods=['GET'])
def register_vote():
    global queue
    print request.args
    queue.register_vote(url=request.args.get('url'),positive=int(request.args.get('positive')),negative=int(request.args.get('negative')),creator=request.remote_addr)
    return 'OK'

if __name__ == '__main__':
    print "Starting Community Playlist"
    app.secret_key = get_app_secret_key()
    app.run(debug=True,host='0.0.0.0')
    #app.run(debug=True)
