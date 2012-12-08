# -*- coding: utf-8 -*-
"""\
Pybit client implemenation for Rhaptos workers.

Author: Michael Mulich
Copyright (c) 2012 Rice University

Parts of this code are derived from the PyBit client implementation at
https://github.com/nicholasdavidson/pybit licensed under GPL2.1.

This software is subject to the provisions of the GNU Lesser General
Public License Version 2.1 (LGPL).  See LICENSE.txt for details.
"""
import pika
import pybit


class Client(object):
    """Generic client implementation for a delegator of worker/drone process
    trigger by a queued entry.

    """

    def __init__(self, architecture, distribution, format, suites, amqp_info):
        self.architecture = architecture
        self.distribution = distribution
        self.format = format

        # We subscribe to a list of queues based on the parameters
        #   passed in to the client. The suite list is used to
        #   populate the queue names.
        self._queue_list = dict()
        for suite in suites:
            name = pybit.get_build_queue_name(self.distribution, self.arch,
                                              suite, self.format)
            self._queue_list[suite] = name

        self._amqp_info = amqp_info
        # Message queue storage attributes. These values get set when
        #   the connection is initialized and a queue has a list of
        #   work to be done.
        self._connection = None
        self._channel = None

    def act(self):
        """Rolls through the pipeline"""
        msg = None
        if self._channel is not None:
            for suite in self._listen_list:
                queue = self._listen_list[suite]['queue']
                msg = self._channel.basic_get(queue=queue)
                if msg:
                    break
            if msg is not None :
                logging.info("DO WORK HERE...")
        # FIXME Currently, the additional commands entry that comes
        #       in the job/build request is not handled here.

    def republish(self, job):
        """Republish the job onto the queue. This is usually triggered when
        something wasn't ready and under normal circumstances the job would
        be successful.

        """
        return NotImplemented

    # ############################ #
    #   Connection State Methods   #
    # ############################ #

    def connect(self):
        """Connect to the message queue using the information passed into
        the class at instantiation.

        .. todo:: Document the AMQP setting information key/value pairs after
           we have worked out all the information that we need.

        """
        host = self._amqp_info.get('host', 'localhost')
        port = int(self._amqp_info.get('port', 5672))
        user = self._amqp_info.get('user')
        password = self._amqp_info.get('password')
        virtual_host = self._amqp_info.get('virtual_host')

        credentials = pika.PlainCredentials(user, password)
        connection_parameters = pika.ConnectionParameters(
                host, port, virtual_host, credentials)

        self._connnnection = pika.BlockingConnection(connection_parameters)
        self._channel = self._connection.channel()

        for suite, info in self._queue_list.iteritems():
            queue = info['queue']
            route = info['route']
            logging.debug("Creating queue with name:" + queue)
            self._channel.queue_declare(queue=info,
                                        durable=True, exclusive=False,
                                        auto_delete=False)
            self._channel.queue_bind(exchange=pybit.exchange_name,
                                     queue=queue, routing_key=route)

    def disconnect(self):
        try:
            try:
                self._channel.close()
            except (AttributeError, socket.error):
                pass
            self._connection.close()
        except socket.error :
            pass

    # ############################# #
    #   Context Management methods  #
    # ############################# #

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, type, value, traceback):
        self.disconnect()
