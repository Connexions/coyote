# -*- coding: utf-8 -*-
# ###
# Copyright (c) 2013, Rice University
# This software is subject to the provisions of the GNU Affero General
# Public License version 3 (AGPLv3).
# See LICENCE.txt for details.
# ###

import acmeio
import coyote
import jsonpickle
import pika
import unittest

try:
    from unittest import mock
except ImportError:
    import mock
      
class CoyoteTests(unittest.TestCase):

    def setUp(self):
        # connect to the server
        credentials = pika.PlainCredentials('guest', 'guest')
        parameters = pika.ConnectionParameters('localhost', 5672, None,
                                           credentials)
        connection = pika.BlockingConnection(parameters)
        self.channel = connection.channel()
        
    def tearDown(self):
        self.channel.close()
        
    def test_parse_runner_line(self):
        line = 'python!acmeio.api:status'
        line2 = 'python!jsonpickle:decode'
        runner = coyote.parse_runner_line(line)
        runner2 = coyote.parse_runner_line(line2)
        # make sure something callable was returned
        self.assertTrue(hasattr(runner, '__call__'))
        self.assertTrue(hasattr(runner2, '__call__'))
        # and that it has the right name
        self.assertEquals(runner.__name__, 'status')
        self.assertEquals(runner2.__name__, 'decode')
        
    def test_set_status(self):
        # make the mock request
        mock_request = mock.Mock()
        mock_request.get_job_id.return_value = 45
        
        # make a mock config
        mock_config = mock.Mock()
        mock_config.amqp = {'host': 'localhost', 
                            'port':5672, 
                            'user': 'guest', 
                            'password':'guest', 
                            'virtual_host': None}
        
        with mock.patch('coyote.config', mock_config):
            coyote.set_status('testing', mock_request)
        
        # check that the right thing was put on the queue
        queue = 'acme-status'
        self.channel.queue_declare(queue=queue, durable=True)
        tag = self.channel.basic_get(queue=queue, no_ack=True)
        message = jsonpickle.decode(tag[-1])
        self.assertEquals(message['job'], 45)
        self.assertEquals(message['status'], 'testing')
        
    def test_republish(self):
        # create a build request
        build_string = '{"py/object": "pybit.models.BuildRequest",\
        "timestamp": null, "job": {"py/object": "pybit.models.Job",\
        "packageinstance": {"py/object": "pybit.models.PackageInstance",\
        "format": {"py/object": "pybit.models.Format", "id": 5,\
        "name": "completezip"}, "package": {"py/object": "pybit.models.Package",\
        "version": "1.2", "id": 2, "name": "col10642"}, "id": 1,\
        "master": true, "suite": {"py/object": "pybit.models.Suite",\
        "id": 3, "name": "latex"}, "distribution": {"py/object": \
        "pybit.models.Dist", "id": 2, "name": "cnx"}, "arch": \
        {"py/object": "pybit.models.Arch", "id": 9, "name": "desktop"},\
        "build_env": null}, "id": 36, "buildclient": null}, "transport": \
        {"py/object": "pybit.models.Transport", "uri": "http://cnx.org/", \
        "id": null, "vcs_id": "", "method": ""}, "web_host": "localhost:8080"}'
        build_request = jsonpickle.decode(build_string)

        # republish
        queue = 'cnx_desktop_latex_completezip'
        self.channel.queue_declare(queue=queue)
        coyote.republish(build_request, queue, self.channel)
        
        # get it off the queue and test it
        tag = self.channel.basic_get(queue=queue, no_ack=True)
        build_request = jsonpickle.decode(tag[-1])
        job_id = build_request.get_job_id()
        self.assertEquals(job_id, 36)
        package = build_request.get_package()
        self.assertEquals(package, 'col10642')
        version = build_request.get_version()
        self.assertEquals(version, '1.2')