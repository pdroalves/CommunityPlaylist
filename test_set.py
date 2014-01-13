#!/usr/bin/python
# -*- coding: utf-8 -*-

import random
import unittest
import os
import time
import string
import tempfile
from queue_manager import QueueManager

db_path=tempfile.gettempdir()

class TestSequenceFunctions(unittest.TestCase):

    def setUp(self):
        path=db_path+"/"+''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(8))
        self.queue =  QueueManager(database=path)

    #def tearDown(self):
    #    os.remove(db_path)

    def test_db_connection(self):
        print "Test 1"
        self.assertIsNotNone(self.queue.get_db_connection())

    def test_check_initial_emptiness(self):
        print "Test 2"
        self.assertEqual(len(self.queue.getQueue()),0)

    def test_add_item(self):
        print "Test 2"

        self.queue.add(url="tGiEsjtfJdg",creator="127.0.0.1")
        self.assertEqual(len(self.queue.getQueue()),1)

    def test_rm_item(self):
        print "Test 3"

        self.queue.rm(url="tGiEsjtfJdg")
        self.assertEqual(len(self.queue.getQueue()),0)

    def test_uniqueness(self):
        print "Test 4"

        self.queue.add(url="tGiEsjtfJdg",creator="127.0.0.1")
        self.queue.add(url="tGiEsjtfJdg",creator="127.0.0.1")
        self.queue.add(url="tGiEsjtfJdg",creator="127.0.0.2")
        self.assertEqual(len(self.queue.getQueue()),1)

    def test_next_video(self):
        print "Test 5"
        count = 0
        added = []

        new_item,done = self.queue.add(url="tGiEsjtfJdg",creator="127.0.0.1")
        if done:
            count += 1
            added.append("tGiEsjtfJdg")
        new_item,done = self.queue.add(url="XFwVfrAURDg",creator="127.0.0.1")
        if done:
            count += 1
            added.append("XFwVfrAURDg")
        new_item,done = self.queue.add(url="EfuVcRdamCY",creator="127.0.0.1")
        if done:
            count += 1
            added.append("EfuVcRdamCY")
        new_item,done = self.queue.add(url="vw3-dijOCK0",creator="127.0.0.1")
        if done:
            count += 1
            added.append("vw3-dijOCK0")
        
        iterator = 0
        for index,item in enumerate(added):
            self.assertEqual(len(self.queue.getQueue()),count-index)
            self.assertEqual(self.queue.next(),added[index])

        self.assertEqual(len(self.queue.getQueue()),0)
        self.assertEqual(self.queue.next(),None)

    def test_votes(self):
        print "Test 6"
        added = []
        count = 0

        # Asserts that it cant register a vote to something that isn't there
        self.assertFalse(self.queue.register_vote(url="dummy",
                            positive=1,
                            negative=0,
                            creator="127.0.0.1"))

        # Asserts votes for queues of a single item 
        new_item,done = self.queue.add(url="tGiEsjtfJdg",creator="127.0.0.1")
        if done:
            count += 1
            added.append("tGiEsjtfJdg")

        elements = self.queue.getQueue()
        for element in elements:
            self.assertIsNotNone(element)
            self.assertEqual(element.get("positive"),1)
            self.assertEqual(element.get("negative"),0)

        self.assertIsNotNone(self.queue.register_vote(url="tGiEsjtfJdg",
                            positive=1,
                            negative=0,
                            creator="127.0.0.2"))

        elements = self.queue.getQueue()
        self.assertEqual(len(elements),1)

        element = [x for x in elements if x.get("url") == "tGiEsjtfJdg"][0]
        self.assertIsNotNone(element)
        self.assertEqual(element.get("positive"),2)
        self.assertEqual(element.get("negative"),0)

        # Asserts votes for bigger queues
        new_item,done = self.queue.add(url="XFwVfrAURDg",creator="127.0.0.1")
        if done:
            count += 1
            added.append("XFwVfrAURDg")
        new_item,done = self.queue.add(url="EfuVcRdamCY",creator="127.0.0.1")
        if done:
            count += 1
            added.append("EfuVcRdamCY")
        new_item,done = self.queue.add(url="vw3-dijOCK0",creator="127.0.0.1")
        if done:
            count += 1
            added.append("vw3-dijOCK0")

        self.assertIsNotNone(self.queue.register_vote(url="tGiEsjtfJdg",
                            positive=0,
                            negative=1,
                            creator="127.0.0.2"))
        self.assertIsNotNone(self.queue.register_vote(url="XFwVfrAURDg",
                            positive=1,
                            negative=0,
                            creator="127.0.0.2"))
        self.assertIsNotNone(self.queue.register_vote(url="EfuVcRdamCY",
                            positive=1,
                            negative=0,
                            creator="127.0.0.2"))
        self.assertIsNotNone(self.queue.register_vote(url="vw3-dijOCK0",
                            positive=1,
                            negative=0,
                            creator="127.0.0.2"))

        elements = self.queue.getQueue()
        self.assertEqual(len(elements),count)
        
        for element in elements:
            if  element.get("url") == "tGiEsjtfJdg":
                self.assertEqual(element.get("positive"),1)
                self.assertEqual(element.get("negative"),1)
            elif  element.get("url") == "XFwVfrAURDg":
                self.assertEqual(element.get("positive"),2)
                self.assertEqual(element.get("negative"),0)
            elif  element.get("url") == "tGiEsjtfJdg":
                self.assertEqual(element.get("positive"),2)
                self.assertEqual(element.get("negative"),0)
            elif  element.get("url") == "vw3-dijOCK0":
                self.assertEqual(element.get("positive"),2)
                self.assertEqual(element.get("negative"),0)

    def test_starvation1(self):
        print "Test 7"

        self.queue.set_pause(True)
        self.queue.queue.extend([{
                            "id":1,
                            "url":'dummy1',
                            "added_at":int(time.time()),
                            "playtime":1,   
                            "voters":{
                                "positive":[1],
                                "negative":[0]
                            },
                            "data":{"title":"dummy1","duration":1}
                            },
                            {
                            "id":2,
                            "url":'dummy2',
                            "added_at":int(time.time()),
                            "playtime":1,   
                            "voters":{
                                "positive":[1],
                                "negative":[0]
                            },
                            "data":{"title":"dummy2","duration":1}
                            }])
        timer = time.time()
        while time.time() - timer < 5:
            self.queue.sort()
            time.sleep(1)

        status,hungry = self.queue.sort()
        self.assertEqual(len(hungry),0)


    def test_starvation2(self):
        print "Test 8"

        self.queue.set_pause(True)
        self.queue.queue.extend([{
                            "id":1,
                            "url":'dummy1',
                            "added_at":int(time.time()),
                            "playtime":3,   
                            "voters":{
                                "positive":1,
                                "negative":0
                            },
                            "data":{"title":"dummy1","duration:":1}
                            },
                            {
                            "id":2,
                            "url":'dummy2',
                            "added_at":int(time.time()),
                            "playtime":3,   
                            "voters":{
                                "positive":1,
                                "negative":0
                            },
                            "data":{"title":"dummy2","duration:":1}
                            },
                            {
                            "id":3,
                            "url":'dummy3',
                            "added_at":int(time.time()),
                            "playtime":3,   
                            "voters":{
                                "positive":1,
                                "negative":0
                            },
                            "data":{"title":"dummy3","duration:":1}
                            }])
        self.queue.set_pause(False)



if __name__ == '__main__':
    unittest.main()