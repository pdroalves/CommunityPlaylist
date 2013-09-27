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
#       Pedro Alves, pdroalves@gmail.com
#               28 August, 2013 - Campinas,SP - Brazil

import sqlite3
from flask import _app_ctx_stack

db = None

class QueueManager:
	def __init__(self,database='database.db'):
		self.queue = []
		self.db_file = database
		#self.sync()

	def get_db(self):
		global db 

		top = _app_ctx_stack.top
		db_file = self.db_file
		if db is None:
			print 'Criando'
			sqlite_db = sqlite3.connect(db_file)
			cursor = sqlite_db.cursor()

			db = sqlite_db

			cursor.execute('CREATE TABLE IF NOT EXISTS playlist (id INTEGER PRIMARY KEY,url TEXT,played INTEGER DEFAULT 0,removed INTEGER DEFAULT 0)')
			history = cursor.execute('SELECT id,url FROM playlist WHERE played = 0 and removed = 0  ORDER BY id ASC')

			for h in history:

				self.queue.append({
									"id":h[0],
									"url":h[1]
									})
		return db
	def commit(self):
		self.get_db().commit()
		return

	def __exit__(self, type, value, traceback):
		db = get_db()
		db.commit()
		db.close

	def add(self,url):
		cursor = self.get_db().cursor()
		if not [element for element in self.queue if element['url'] == url]:
			cursor.execute('INSERT INTO playlist (url) VALUES(\''+url+'\')')
			id = cursor.execute('SELECT id FROM playlist WHERE url = \''+url+'\' and removed = 0 ORDER BY id DESC LIMIT 1').fetchone()
			self.queue.append({
								"id":id,
								"url":url
								})
		self.commit()
		return

	def rm(self,url):
		cursor = self.get_db().cursor()
		element = None
		for item in self.queue:
			if item.get('url') == url:
				element = item
				break

		if element is not None:
			print element
			self.queue.remove(element)
			cursor.execute('UPDATE playlist SET removed = 1 WHERE id = \''+str(element.get("id"))+'\'')
			self.commit()
		return

	def next(self):
		cursor = self.get_db().cursor()
		if(len(self.queue) > 0):
			next_element = self.queue[0]
			self.queue.remove(next_element)
			cursor.execute('UPDATE playlist SET played = 1 WHERE id = \''+str(next_element.get("id"))+'\'')
			self.commit()
			print "Tocando "+next_element.get("url")
			return next_element.get("url")
		else:
			return None

	def sync(self):
		cursor = self.get_db().cursor()

		## Esvazia fila
		for element in self.queue:
			self.queue.remove(element)

		## Repovoa fila
		data = cursor.execute('SELECT id,url FROM playlist where removed = 0 ORDER BY id ASC').fetchall()

		for d in data:
			element = {
						"id":d[0],
						"url":d[1]
					  }
			if element not in self.queue:
				self.queue.append(element)

	def getQueue(self):
		self.get_db()
		q = []
		for x in self.queue:
			q.append(x['url'])
		return q

	def clear(self):
		cursor = self.get_db().cursor()
		while len(self.queue) > 0:
			for element in self.queue:
				print 'Clear: '+str(element)
				self.rm(element.get('url'))
		return
