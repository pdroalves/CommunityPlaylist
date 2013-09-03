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


class QueueManager:
	def __init__(self):
		self.queue = []

	def add(self,element):
		if element not in self.queue:
			self.queue.append(element)
		return

	def rm(self,element):
		if element in self.queue:
			self.queue.remove(element)
		return

	def next(self):
		if(len(self.queue) > 0):
			next_element = self.queue[0]
			self.queue.remove(next_element)
			return next_element
		else:
			return None

	def getQueue(self):
		return self.queue

	def clear(self):
		for element in self.queue:
			print 'Clear: '+element
			self.queue.remove(element)
		return
