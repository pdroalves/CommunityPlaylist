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
import logging
logger = logging.getLogger("DBManager")


class DatabaseManager:
	def __init__(self,database='database.db'):
		self.db_file = database
		self.db = None
		self.conn = None
		logger.info("Database manager started")

	def __exit__(self, type, value, traceback):
		db = self.get_db()
		db.commit()
		db.close()
		logger.info("Database manager finished")

	def __get_db_connection(self):
		db = sqlite3.connect(self.db_file)
		self.__create_db(db=db)
		return db

	def get_db(self):
		if self.db is None:
			self.db = self.__get_db_connection()
		return self.db

	def __create_db(self,db):
		assert db is not None
		cursor = db.cursor()
		cursor.execute('CREATE TABLE IF NOT EXISTS playlist (id INTEGER PRIMARY KEY,url TEXT,played INTEGER DEFAULT 0,removed INTEGER DEFAULT 0)')
		cursor.execute('CREATE TABLE IF NOT EXISTS vote_history (id INTEGER PRIMARY KEY,url INTEGER NOT NULL,tag TEXT NOT NULL,positive INTEGER DEFAULT 0,negative INTEGER DEFAULT 0)')

	def commit(self):
		self.get_db().commit()
		logger.info("Commit")
		return