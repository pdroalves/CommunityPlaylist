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
import time
from flask import _app_ctx_stack
from youtube_handler import YoutubeHandler

db = None

class QueueManager:
	def __init__(self,database='database.db'):
		self.queue = []
		self.db_file = database
		#self.sync()
		self.yth = YoutubeHandler()

	def __exit__(self, type, value, traceback):
		db = self.get_db()
		db.commit()
		db.close()

	def calc_playtime(self,url):
		# Calculate how long until this song start to play without any queue order change
		candidates = [x for x in self.queue if x.get('url') == url]

		# Assert this url is in queue
		if len(candidates) > 0:
			index = self.queue.index(candidates[0])
			playtime = 0

			for i in range(index):
				playtime = playtime + int(self.queue[i].get('data').get('duration'))
			return playtime
		return -1

	def calc_full_playtime(self):
		queue_length = len(self.queue)
		if queue_length > 0:
			return self.calc_playtime(url=self.queue[queue_length-1])
		else:
			return 0

	def get_db(self):
		global db 

		top = _app_ctx_stack.top
		db_file = self.db_file
		if db is None:
			sqlite_db = sqlite3.connect(db_file)
			cursor = sqlite_db.cursor()

			db = sqlite_db

			cursor.execute('CREATE TABLE IF NOT EXISTS playlist (id INTEGER PRIMARY KEY,url TEXT,positive INTEGER DEFAULT 1,negative DEFAULT 0,played INTEGER DEFAULT 0,removed INTEGER DEFAULT 0)')
			history = cursor.execute('SELECT id,url,positive,negative FROM playlist WHERE played = 0 and removed = 0  ORDER BY id ASC')

			for h in history:
				id = h[0]
				url = h[1]
				positive_votes = h[2]
				negative_votes = h[3]
				ytData = self.yth.get_info(h[1]).json()

				self.queue.append({
									"id":id,
									"url":url,
									"added_at":int(time.time()),
									"playtime":self.calc_full_playtime(),				
									"votes":{
										"positive":int(positive_votes),
										"negative":int(negative_votes)
									},
									"data":ytData.get('data')
									})
		return db

	def add(self,url):
		cursor = self.get_db().cursor()
		new_item = None
		if not [element for element in self.queue if element['url'] == url]:
			cursor.execute('INSERT INTO playlist (url,positive,negative) VALUES(\''+url+'\',1,0)')
			id = cursor.execute('SELECT id FROM playlist WHERE url = \''+url+'\' and removed = 0 ORDER BY id DESC LIMIT 1').fetchone()
			ytData = self.yth.get_info(url).json()
			data = ytData.get('data')

			new_item = {
							"id":id,
							"url":url,
							"added_at":int(time.time()),
							"votes":{
								"positive":1,
								"negative":0
							},
							"data":ytData.get('data')
						}
			self.queue.append(new_item)
		self.commit()
		return new_item

	def rm(self,url):
		cursor = self.get_db().cursor()
		candidates = [item for item in self.queue if item.get('url') == url]

		if len(candidates) > 0:
			element = candidates = [0]
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
			url = next_element.get("url")
			return url
		else:
			return None

	def register_vote(self,url,positive,negative):
		if type(positive) == int and type(negative) == int:
			cursor = self.get().cursor()
			candidates = [item for item in self.queue if item.get('url') == url]

			if len(candidates) > 0:
				element = candidates[0]

				# Update votes
				votes = element.get("votes")
				votes.update({
							"positive":votes.get("positive")+positive,
							"negative":votes.get("negative")+negative
							})

				element.update({"votes":votes})
				cursor.execute('UPDATE playlist SET positive = positive + '+str(positive)+', negative = negative + '+str(negative)+' where id = '+str(element.get('id')))
		return

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
		queue = [{
					"url":element.get('url'),
					"title":element.get('data').get('title'),
					"duration":element.get('data').get('duration')
				} for element in self.queue]
		return queue

	def clear(self):
		cursor = self.get_db().cursor()
		while len(self.queue) > 0:
			for element in self.queue:
				print 'Clear: '+str(element)
				self.rm(element.get('url'))
		return

	def sort(self,playtime_percent_warning=1.5):
		# Ordena a fila de acordo com o tempo de espera e a quantidade de votos
		return 


	def commit(self):
		self.get_db().commit()
		return