# -*- coding: utf-8 -*-

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
