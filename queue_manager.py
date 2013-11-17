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
import logging
from flask import _app_ctx_stack
from youtube_handler import YoutubeHandler

db = None

logger = logging.getLogger("QueueManager")

class QueueManager:
	def __init__(self,database='database.db'):
		self.queue = []
		self.db_file = database
		#self.sync()
		self.yth = YoutubeHandler()
		logger.info("Queue started")

	def __exit__(self, type, value, traceback):
		db = self.get_db()
		db.commit()
		db.close()
		logger.info("Queue finished")

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
			db = sqlite3.connect(db_file)
			cursor = db.cursor()

			cursor.execute('CREATE TABLE IF NOT EXISTS playlist (id INTEGER PRIMARY KEY,url TEXT,played INTEGER DEFAULT 0,removed INTEGER DEFAULT 0)')
			cursor.execute('CREATE TABLE IF NOT EXISTS vote_history (id INTEGER PRIMARY KEY,url INTEGER NOT NULL,tag TEXT NOT NULL,positive INTEGER DEFAULT 0,negative INTEGER DEFAULT 0)')
			history = cursor.execute('SELECT id,playlist.url FROM playlist WHERE played = 0 and removed = 0  ORDER BY id ASC').fetchall()
			voters_history = {}
			voters = cursor.execute("SELECT vh.url,tag,positive,negative FROM vote_history vh INNER JOIN playlist p ON p.url = vh.url WHERE played = 0 and removed = 0 GROUP BY tag HAVING MAX(vh.id)").fetchall()		
			
			for voter in voters:
				url = voter[0]
				tag = voter[1]
				positive = voter[2]
				negative = voter[3]

				if not voters_history.has_key(url):
					voters_history.update({url:{"positive":[],"negative":[]}})

				if positive > 0 and tag not in voters_history.get(url).get("positive"):
					voters_history.get(url).get("positive").append(tag)
					if tag in voters_history.get(url).get("negative"):
						voters_history.get(url).get("negative").remove(tag)
				if negative > 0 and tag not in voters_history.get(url).get("negative"):
					voters_history.get(url).get("negative").append(tag)	
					if tag in voters_history.get(url).get("positive"):
						voters_history.get(url).get("positive").remove(tag)					

			for h in history:
				print h
				id = h[0]
				url = h[1]
				ytData = self.yth.get_info(url).json()

				self.queue.append({
									"id":id,
									"url":url,
									"added_at":int(time.time()),
									"playtime":self.calc_full_playtime(),	
									"voters":{
										"positive":voters_history.get(url).get("positive"),
										"negative":voters_history.get(url).get("negative")
									},
									"data":ytData.get('data')
									})
			logger.info("DB loaded:\n\t"+str(self.queue))
		return db

	def add(self,url,creator):
		cursor = self.get_db().cursor()
		new_item = None
		if not [element for element in self.queue if element['url'] == url]:
			cursor.execute("INSERT INTO playlist (url) VALUES(\'%s\')" % url)
			print creator
			cursor.execute("INSERT INTO vote_history (url,tag,positive) VALUES(\'%s\',\'%s\',1)" % (url,str(creator)))
			id = cursor.execute('SELECT id FROM playlist WHERE url = \''+url+'\' and removed = 0 ORDER BY id DESC LIMIT 1').fetchone()
			ytData = self.yth.get_info(url).json()
			data = ytData.get('data')

			new_item = {
							"id":id,
							"url":url,
							"added_at":int(time.time()),
							"playtime":self.calc_full_playtime(),
							"voters":{
								"positive":[creator],
								"negative":[]
							},
							"data":ytData.get('data')
						}
			self.queue.append(new_item)
			logger.info("Item added: "+str(new_item))
		self.commit()
		return new_item

	def rm(self,url):
		cursor = self.get_db().cursor()
		candidates = [item for item in self.queue if item.get('url') == url]
		if len(candidates) > 0:
			element = candidates[0]
			self.queue.remove(element)
			cursor.execute('UPDATE playlist SET removed = 1 WHERE id = \''+str(element.get("id"))+'\'')
			self.commit()
			logger.info("Item removed: "+str(element))
		return

	def next(self):
		cursor = self.get_db().cursor()
		if(len(self.queue) > 0):
			next_element = self.queue[0]
			self.queue.remove(next_element)
			cursor.execute('UPDATE playlist SET played = 1 WHERE id = \''+str(next_element.get("id"))+'\'')
			self.commit()
			print "Tocando "+next_element.get("url")
			logger.info("Next song: "+str(next_element.get("url")))
			url = next_element.get("url")
			return url
		else:
			return None

	def register_vote(self,url,positive,negative,creator):
		assert type(creator) == str
		if type(positive) == int and type(negative) == int:
			cursor = self.get_db().cursor()
			candidates = [item for item in self.queue if item.get('url') == url]

			if len(candidates) > 0:
				element = candidates[0]

				# Update voters
				voters = element.get("voters")
				if positive > 0 and creator not in voters.get("positive"):
					voters.get("positive").append(creator)
					if creator in voters.get("negative"):
						voters.get("negative").remove(creator)
				if negative > 0 and creator not in voters.get("negative"):
					voters.get("negative").append(creator)
					if creator in voters.get("positive"):
						voters.get("positive").remove(creator)

				element.update({"voters":voters})
				cursor.execute("INSERT INTO vote_history (url,tag,positive,negative) VALUES (\'%s\',\'%s\',%s,%s)" % (url,creator,str(positive),str(negative)))
				self.commit()
				logger.info("Updating votes for "+str(element.get("url"))+": "+str(voters))
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
					"duration":element.get('data').get('duration'),
					"positive":len(element.get('voters').get('positive')),
					"negative":len(element.get('voters').get('negative'))
				} for element in self.queue]
		return queue

	def clear(self):
		cursor = self.get_db().cursor()
		while len(self.queue) > 0:
			for element in self.queue:
				print 'Clear: '+str(element)
				self.rm(element.get('url'))
		logger.info("Queue cleared...")
		return

	def __custom_sort(self,starvation_rate=2):
		lambda_votes = lambda x:len(x.get("voters").get("positive"))-len(x.get("voters").get("negative"))
		lambda_starvation = lambda x: time.time() - x.get("added_at")-x.get("playtime")*starvation_rate

		hungry = [x for x in self.queue if lambda_starvation(x) > 0]

		if len(hungry) > 1:
			for x,y in zip(hungry,hungry[1:]):
				self.queue[self.queue.index(x)+1:self.queue.index(y)-1] = sorted(self.queue[self.queue.index(x)+1:self.queue.index(y)-1],key=lambda_votes,reverse=True)
		elif len(hungry) == 1:
			x = hungry[0]
			self.queue[0:self.queue.index(x)-1] = sorted(self.queue[0:self.queue.index(x)-1],key=lambda_votes,reverse=True)
			self.queue[self.queue.index(x)+1:len(self.queue)] = sorted(self.queue[self.queue.index(x)+1:len(self.queue)],key=lambda_votes,reverse=True)
		else:
			self.queue[0:len(self.queue)] = sorted(self.queue[0:len(self.queue)],key=lambda_votes,reverse=True)	
		logger.info("Sorting queue")	

	def sort(self):
		# Ordena a fila de acordo com o tempo de espera e a quantidade de votos
		lambda_votes = lambda x:len(x.get("voters").get("positive"))-len(x.get("voters").get("negative"))
		self.__custom_sort()
		#print [{"url":x.get("url"),"votes":lambda_votes(x)} for x in self.queue]
		return 


	def commit(self):
		self.get_db().commit()
		logger.info("Commit")
		return
