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
#       Pedro Alves, pdroalves@gmail.com
#               10 November, 2013 - Campinas,SP - Brazil

import requests
import json
import logging
import time

logger = logging.getLogger("YTH")
class YoutubeHandler:
	def __init__(self,api_url=['http://gdata.youtube.com/feeds/api/videos/','?v=2&alt=jsonc']):
		assert len(api_url) == 2
		self.api_url = api_url
		
	def get_info(self,id,max_repeats=10):
		count = 0
		while count < max_repeats:
			try:
				r = requests.get(self.api_url[0]+id+self.api_url[1])
				status = r.status_code
				#headers = r.headers['content_type']
				#encoding = r.encoding
				text = r.text
				data = r.json()
				if status == 200:
					return data
				else:
					logger.critical("Requests error for url %s: status %d" %((str(id)),status))
				count = max_repeats
				time.sleep(1)
			except Exception,err:
				logger.info(err)
				print "Id: %s ==> %s" % (id,err)
				print "Id: %s ==> %d" % (id,status)
				time.sleep(1)
				count += 1
