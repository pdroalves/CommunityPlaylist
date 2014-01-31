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
import string
from flask import _app_ctx_stack
from youtube_handler import YoutubeHandler
from database_manager import DatabaseManager


logger = logging.getLogger("QueueManager")

class QueueManager:
	def __init__(self,database='database.db'):
		self.queue = []
		self.db_manager = DatabaseManager(database=database)
		self.conn = None
		#self.sync()
		self.yth = YoutubeHandler()
		self.__start_pause_ts=0
		logger.info("Queue started")

	def __exit__(self, type, value, traceback):
		db = self.get_db()
		db.commit()
		db.close()
		logger.info("Queue finished")

	def calc_playtime(self,url,min_starvation_time=1200):
		# Calculate how long until this song start to play without any queue order change
		assert type(url) == str
		candidates = [x for x in self.queue if x.get('url') != url]
		playtime = 0
		
		for candidate in candidates:
			try:
				playtime += candidate.get("data").get("duration")
			except Exception,err:
				if candidate is None:
					logger.critical("Candidate is null.\n\t%s" % candidates)
				elif not candidate.has_key("data"):
					logger.critical("Candidate %s doesn't have 'data' field" % candidate)
				elif type(candidate.get("data")) != dict:
					logger.critical("Candidate 'data' is weird. It is not a dict.")
				elif not candidate.get("data").has_key("duration"):
					logger.critical("Candidate %s doesn't have 'duration' field" % candidate)
				logger.critical(str(err))
		return max(playtime,min_starvation_time)


	def calc_full_playtime(self):
		queue_length = len(self.queue)
		if queue_length > 0:
			return self.calc_playtime(url=str(self.queue[queue_length-1].get("url")))
		else:
			return 0


	def get_db(self):
		top = _app_ctx_stack.top
		if self.conn is None:
			print "Starting database."
			self.conn = self.db_manager.get_db()
			self.conn.isolation_level = None
			cursor = self.conn.cursor()

			history = cursor.execute('SELECT id,playlist.url FROM playlist WHERE played = 0 and removed = 0  ORDER BY id ASC').fetchall()
			voters_history = {}
			voters = cursor.execute("SELECT vh.url,tag,positive,negative FROM vote_history vh INNER JOIN (SELECT MAX(id) id FROM vote_history GROUP BY url,tag) max_vh ON max_vh.id = vh.id INNER JOIN playlist p ON p.url = vh.url WHERE played = 0 and removed = 0").fetchall()		
			
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

			txt = "Votes founded: %d"%len(voters_history.keys())
			print txt
			logger.info(txt)
			print history
			for h in history:
				print h
				id = h[0]
				url = filter(lambda x: x in string.printable,h[1])
				if voters_history.has_key(url):
					positive_voters = voters_history.get(url).get("positive")
					negative_voters = voters_history.get(url).get("negative")
				else:
					logger.info("No votes for "+str(url))
					positive_voters = []
					negative_voters = []

				# The need to receive data from Youtube makes this step slow
				data = self.yth.get_info(url) 
				try:
					if type(data) is not dict:
						ytData = data.json()
					else:
						ytData = data

					self.queue.append({
									"id":id,
									"url":url,
									"added_at":int(time.time()),
									"playtime":self.calc_full_playtime(),	
									"voters":{
										"positive":positive_voters,
										"negative":negative_voters
									},
									"data":ytData.get('data')
									})
				except Exception,err:
					txt ="Url: %s - Data: %s" % (url,str(data))
					logger.critical(str(err))
					logger.critical(txt)
					self.conn.commit()
			logger.info("DB loaded:\n\t"+str(self.queue))
		return self.conn

	def add(self,url,creator):
		db = self.get_db()
		cursor = db.cursor()
		new_item = None
		done = False
		if not [element for element in self.queue if element['url'] == url]:
			cursor.execute("INSERT INTO playlist (url) VALUES(\'%s\')" % url)
			print creator
			cursor.execute("INSERT INTO vote_history (url,tag,positive) VALUES(\'%s\',\'%s\',1)" % (url,str(creator)))
			id = cursor.execute('SELECT id FROM playlist WHERE url = \''+url+'\' and removed = 0 ORDER BY id DESC LIMIT 1').fetchone()
			data = self.yth.get_info(url)
			if data is not None:
				if not type(data) == dict:
					ytData = data.json()
				else:
					ytData = data
				#print ytData.get("data").get("title")
				try:
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
				except Exception,err:
					logger.critical(str(err))
					logger.critical("Url: %s - Data: %s" % str(url,data))
			else:
				logger.critical("Couldn't add item %s"%url)
		db.commit()
		return new_item

	def rm(self,url):
		assert type(url) == str
		logger.info("Clearing element "+url)
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
		db = self.get_db()
		cursor = db.cursor()
		if(len(self.queue) > 0):
			next_element = self.queue[0]
			self.queue.remove(next_element)
			cursor.execute('UPDATE playlist SET played = 1 WHERE id = \''+str(next_element.get("id"))+'\'')
			db.commit()
			print "Tocando "+next_element.get("url")
			logger.info("Next song: "+str(next_element.get("url")))
			url = next_element.get("url")
			return url
		else:
			return None

	def register_vote(self,url,positive,negative,creator):
		assert type(creator) == str
		assert type(positive) == int
		assert type(negative) == int
		try:
			cursor = self.get_db().cursor()
			candidates = [item for item in self.queue if item.get('url') == url]

			assert len(candidates) > 0
			
			element = candidates[0]

			# Update voters
			voters = element.get("voters")
			if positive > 0 and creator not in voters.get("positive"):
				voters.get("positive").append(creator)
				if creator in voters.get("negative"):
					voters.get("negative").remove(creator)
			elif creator in voters.get("positive"):
				raise Exception("Voto  positivo já registrado!")
			if negative > 0 and creator not in voters.get("negative"):
				voters.get("negative").append(creator)
				if creator in voters.get("positive"):
					voters.get("positive").remove(creator)
			elif creator in voters.get("negative"):
				raise Exception("Voto  negativo já registrado!")

			element.update({"voters":voters})
			cursor.execute("INSERT INTO vote_history (url,tag,positive,negative) VALUES (\'%s\',\'%s\',%s,%s)" % (url,creator,str(positive),str(negative)))
			self.commit()
			logger.info("Updating votes for "+str(element.get("url"))+": "+str(voters))
		except Exception,err:
			logger.critical("Error on vote register: \t%s"%str(err))
			return False
		return True

	def update_playtime(self):
		diff = 0
		if self.__start_pause_ts == 0:
			self.__start_pause_ts = time.time()

		if self.paused:
			logger.info("Queue paused")
			if time.time()-self.__start_pause_ts > 2:
				diff = time.time()-self.__start_pause_ts
				self.__start_pause_ts = time.time()
		elif self.__start_pause_ts > 0:
			diff = time.time()-self.__start_pause_ts
			logger.info("Queue resumed") 
			self.__start_pause_ts = 0

		if diff > 0.1:
			for element in self.queue:
				logger.info("Adding %s to %s playtime." % (diff,element.get("url")))
				element.update({"playtime":element.get("playtime")+diff})

	def set_pause(self,paused):
		self.paused = paused
		self.update_playtime()
	
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
		self.get_db() # Just asserts that there is something inside the db
		fila = []
		if len(self.queue) > 0:
			fila += [{
						"url":element.get('url'),
						"title":element.get('data').get('title'),
						"duration":element.get('data').get('duration'),
						"positive":len(element.get('voters').get('positive')),
						"negative":len(element.get('voters').get('negative'))
					} for element in self.queue]
		return fila

	def clear(self):
		logger.info("Clearing list")
		print "Clearing list"
		
		db = self.get_db()# Just asserts that there is something inside the db
		cursor = db.cursor()
		cursor.execute("BEGIN")
		ids = [str(element.get('id')) for element in self.queue]
		print ids
		query = 'UPDATE playlist SET removed = 1 WHERE id in ('+','.join(ids)+')'
		cursor.execute(query)
		
		self.queue = list()
		logger.info("Item removed: "+str(element))
		cursor.execute("COMMIT")
		logger.info("Queue cleared...")
		return

	def __is_starving(self,element,starvation_rate=2,min_starvation_time=0):
		assert element.has_key("added_at")
		assert element.has_key("playtime")
		assert element.has_key("data")
		if not element.get("data").has_key("duration"):
			duration = 120
		else:
			duration = element.get("data").get("duration")

		return time.time() - element.get("added_at")-element.get("playtime")*starvation_rate-duration > min_starvation_time

	def __custom_sort(self,starvation_rate=3):
		self.update_playtime()

		lambda_votes = lambda x:len(x.get("voters").get("positive"))-len(x.get("voters").get("negative"))
		#lambda_starvation = lambda x: self.__is_starving(element=x,starvation_rate=starvation_rate)
		lambda_starvation = lambda x: False
		
		hungry = [x for x in self.queue if lambda_starvation(x)]

		if len(hungry) > 0:
			print ','.join([x.get("data").get("title")+"Playtime: "+str(x.get("playtime"))+" Starvation:"+str(lambda_starvation(x)) for x in hungry])

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
		return True,hungry

	def sort(self):
		# Ordena a fila de acordo com o tempo de espera e a quantidade de votos
		lambda_votes = lambda x:len(x.get("voters").get("positive"))-len(x.get("voters").get("negative"))
		status,hungry=self.__custom_sort()
		return status,hungry
