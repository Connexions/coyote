# -*- coding: utf-8 -*-
# ###
# Copyright (c) 2013, Rice University
# This software is subject to the provisions of the GNU Affero General
# Public License version 3 (AGPLv3).
# See LICENCE.txt for details.
# ###

import jsonpickle
import pika
import signal
import subprocess
import tempfile
import unittest

try:
    from unittest import mock
except ImportError:
    import mock
    
import coyote

artifacts = []
      
class FunctionalTests(unittest.TestCase):
    
    def setUp(self):
        # import and create a TestApp to test requests
        from webtest import TestApp
        self.testapp = TestApp('http://localhost:6543/')
    
    def test_consume(self):

        # put something on the queue
        self.testapp.post('/',
                {
                    'job-type':'cnx.desktop.latex.epub',
                    'id':'col10642', 'version':'1.2', 
                    'url':'http://cnx.org', 
                    'content-url':'http://cnx.org/content/col10642/1.2/',
                    }, status=200)
        
        # connect to the server
        credentials = pika.PlainCredentials('guest', 'guest')
        parameters = pika.ConnectionParameters('localhost', 5672, None,
                                           credentials)
        connection = pika.BlockingConnection(parameters)
        self.channel = connection.channel()
        
        # run coyote
        def signal_handler(signum, frame):
            raise Exception("Timed out!")

        signal.signal(signal.SIGALRM, signal_handler)
        signal.alarm(5)

        try:
            coyote.main(['coyote/tests/test.ini'])
        except Exception:
            pass

        # make sure nothing is on the queue anymore
        queue = 'cnx_desktop_latex_epub'
        queue_obj = self.channel.queue_declare(queue=queue, passive=True)
        self.assertEquals(queue_obj.method.message_count, 0)
        self.assertEquals(queue_obj.method.consumer_count, 1)
        
        # make sure the runner did something
        self.assertEquals(artifacts[0], 'col10642')
        self.assertEquals(artifacts[1], '1.2')
        
        # check status queue
        tag = self.channel.basic_get(queue='acme-status', no_ack=True)
        tag2 = self.channel.basic_get(queue='acme-status', no_ack=True)
        first_status = jsonpickle.decode(tag[-1])
        second_status = jsonpickle.decode(tag2[-1])
        self.assertEquals(first_status['status'], 'Building')
        self.assertEquals(second_status['status'], 'Done')
        self.assertEquals(first_status['job'], second_status['job'])
        self.assertEquals(artifacts[2], first_status['job']) 
