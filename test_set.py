#!/usr/bin/python
# -*- coding: utf-8 -*-

import random
import unittest
import os
from queue_manager import QueueManager

db_path="database_test.db"
class TestSequenceFunctions(unittest.TestCase):

    #def setUp(self):
    #    queue =  QueueManager(database=db_path)

    #def tearDown(self):
    #    os.remove(db_path)

    def test_db_connection(self):
        queue =  QueueManager(database=db_path)

        self.assertIsNotNone(queue.get_db_connection())

    def test_check_initial_emptiness(self):
        queue =  QueueManager(database=db_path)

        self.assertEqual(len(queue.getQueue()),0)

    def test_add_item(self):
        queue =  QueueManager(database=db_path)

        queue.add(url="tGiEsjtfJdg",creator="127.0.0.1")
        self.assertEqual(len(queue.getQueue()),1)

    def test_rm_item(self):
        queue =  QueueManager(database=db_path)

        queue.rm(url="tGiEsjtfJdg")
        self.assertEqual(len(queue.getQueue()),0)

    def test_uniqueness(self):
        queue =  QueueManager(database=db_path)

        queue.add(url="tGiEsjtfJdg",creator="127.0.0.1")
        queue.add(url="tGiEsjtfJdg",creator="127.0.0.1")
        queue.add(url="tGiEsjtfJdg",creator="127.0.0.2")
        self.assertEqual(len(queue.getQueue()),1)

    def test_next_video(self):
        queue =  QueueManager(database=db_path)

        queue.add(url="tGiEsjtfJdg",creator="127.0.0.1")
        queue.add(url="XFwVfrAURDg",creator="127.0.0.1")
        queue.add(url="EfuVcRdamCY",creator="127.0.0.1")
        queue.add(url="vw3-dijOCK0",creator="127.0.0.1")
        
        self.assertEqual(len(queue.getQueue()),4)
        self.assertEqual(queue.next(),"tGiEsjtfJdg")
        self.assertEqual(len(queue.getQueue()),3)
        self.assertEqual(queue.next(),"XFwVfrAURDg")
        self.assertEqual(len(queue.getQueue()),2)
        self.assertEqual(queue.next(),"EfuVcRdamCY")
        self.assertEqual(len(queue.getQueue()),1)
        self.assertEqual(queue.next(),"vw3-dijOCK0")
        self.assertEqual(len(queue.getQueue()),0)
        self.assertIsNone(queue.next())
        self.assertEqual(len(queue.getQueue()),0)

    def test_votes(self):
        queue =  QueueManager(database=db_path)

        # Asserts that it cant register a vote to something that isn't there
        self.assertFalse(queue.register_vote(url="dummy",
                            positive=1,
                            negative=0,
                            creator="127.0.0.1"))

        # Asserts votes for queues of a single item 
        queue.add(url="tGiEsjtfJdg",creator="127.0.0.1")

        elements = queue.getQueue()
        for element in elements:
            self.assertIsNotNone(element)
            self.assertEqual(element.get("positive"),1)
            self.assertEqual(element.get("negative"),0)

        self.assertIsNotNone(queue.register_vote(url="tGiEsjtfJdg",
                            positive=1,
                            negative=0,
                            creator="127.0.0.2"))

        elements = queue.getQueue()
        self.assertEqual(len(elements),1)

        element = [x for x in elements if x.get("url") == "tGiEsjtfJdg"][0]
        self.assertIsNotNone(element)
        self.assertEqual(element.get("positive"),2)
        self.assertEqual(element.get("negative"),0)

        # Asserts votes for bigger queues
        queue.add(url="XFwVfrAURDg",creator="127.0.0.1")
        queue.add(url="EfuVcRdamCY",creator="127.0.0.1")
        queue.add(url="vw3-dijOCK0",creator="127.0.0.1")

        self.assertIsNotNone(queue.register_vote(url="tGiEsjtfJdg",
                            positive=0,
                            negative=1,
                            creator="127.0.0.2"))
        self.assertIsNotNone(queue.register_vote(url="XFwVfrAURDg",
                            positive=1,
                            negative=0,
                            creator="127.0.0.2"))
        self.assertIsNotNone(queue.register_vote(url="EfuVcRdamCY",
                            positive=1,
                            negative=0,
                            creator="127.0.0.2"))
        self.assertIsNotNone(queue.register_vote(url="vw3-dijOCK0",
                            positive=1,
                            negative=0,
                            creator="127.0.0.2"))

        elements = queue.getQueue()
        self.assertEqual(len(elements),4)
        
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



if __name__ == '__main__':
    unittest.main()