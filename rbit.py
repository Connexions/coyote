# -*- coding: utf-8 -*-
"""\
Pybit client implemenation for Rhaptos workers.

Author: Michael Mulich
Copyright (c) 2012 Rice University

Parts of the client code are derived from the PyBit client implementation at
https://github.com/nicholasdavidson/pybit licensed under GPL2.1.

This software is subject to the provisions of the GNU Lesser General
Public License Version 2.1 (LGPL).  See LICENSE.txt for details.
"""
import time
import logging
import argparse
from ConfigParser import ConfigParser

import jsonpickle
import pika
import requests
import pybit


def parse_runner_line(line):
    """Find suitable importers/handlers for the runner line.
    Return a callables for the given line.

    The line is a single string that has been formatted to display
    its processor type and other information that will be passed to the
    processor of said type. For example::

        python!rbitext.decode_build_request:main

    In this line, we are using the python processor type. In this situation,
    the python processor parses the information about the ``!`` exclamation
    to determine where the logic is located.

    The processor type defines what it will do with the contents after the
    exclamation.

    """
    processor_type, info = line.split('!')
    # FIXME Ideally the processors will be defined in some kind of
    #       registry/configuration.
    #       For now the only supported processor is `python`.
    if processor_type != 'python':
        raise NotImplementedError
    module_path, func = info.split(':')
    module = __import__(module_path)
    return getattr(module, func)


class Config(object):
    """A configuration class can hold information about the client, message
    queue, and runner settings.

    """

    def __init__(self, rbit_settings, amqp_settings, runners={}):
        self.rbit = rbit_settings
        self.amqp = amqp_settings
        self._runners = runners

    @classmethod
    def from_file(cls, ini_file):
        """Used to initialize the configuration object from an INI file."""
        config = ConfigParser()
        if hasattr(ini_file, 'read'):
            config.readfp(ini_file)
        else:
            with open(ini_file, 'r') as f:
                config.readfp(f)

        def config_to_dict(c):
            result = {}
            for section in c.sections():
                result[section] = dict(c.items(section))
            return result

        all_settings = config_to_dict(config)
        rbit_settings = all_settings['rbit']
        amqp_settings = all_settings['amqp']
        del all_settings['rbit']
        del all_settings['amqp']
        runners = all_settings
        return cls(rbit_settings, amqp_settings, runners)

    @property
    def rbit_suites(self):
        """Parse the configured suites to a list."""
        return [s.strip() for s in self.rbit['suites'].split(',')]


class Client(object):
    """Generic client implementation for a delegator of worker/drone process
    trigger by a queued entry.

    """

    def __init__(self, architecture, distribution, format, suites,
                 amqp_info, runner_settings={}):
        self.architecture = architecture
        self.distribution = distribution
        self.format = format

        # We subscribe to a list of queues based on the parameters
        #   passed in to the client. The suite list is used to
        #   populate the queue names.
        self._queue_list = dict()
        for suite in suites:
            queue = pybit.get_build_queue_name(self.distribution,
                                               self.architecture,
                                               suite, self.format)
            route = pybit.get_build_queue_name(self.distribution,
                                               self.architecture,
                                               suite, self.format)
            self._queue_list[suite] = {'queue': queue, 'route': route}

        self._amqp_info = amqp_info
        # Message queue storage attributes. These values get set when
        #   the connection is initialized and a queue has a list of
        #   work to be done.
        self._connection = None
        self._channel = None

        self._runner_settings = runner_settings

    @classmethod
    def from_config(cls, config):
        """Initialize the class using an `rbit.Config` instance."""
        return cls(config.rbit['architecture'], config.rbit['distribution'],
                   config.rbit['format'], config.rbit_suites, config.amqp,
                   # XXX Just making this work. Ideally the config
                   #     object would spit out a list of Pipeline objects.
                   config._runners)

    def _set_status(self, status, build_request):
        payload = {'status': status}
        job_status_url = "http://{0}/job/{1}".format(build_request.web_host,
                                                     build_request.get_job_id())
        try:
            # XXX Hard coded PyBit credentials.
            requests.put(job_status_url, payload,
                         auth=requests.auth.HTTPBasicAuth('admin', 'pass'))
        except requests.exceptions.ConnectionError:
            pass
        else:
            logging.debug("Couldn't find status or current_request")

    def act(self):
        """Rolls through the pipeline"""
        method, header, msg_body = (None, None, None,)
        current_queue = None

        def set_status(status, message=''):
            build_request = jsonpickle.decode(msg_body)
            self._set_status(status, build_request)

        if self._channel is not None:
            for suite in self._queue_list:
                queue = self._queue_list[suite]['queue']
                method, header, msg_body = self._channel.basic_get(queue=queue)
                if msg_body:
                    current_queue = queue
                    break
            if msg_body is not None:
                # XXX This will need refactored. To much raw data work.
                settings = self._runner_settings[current_queue]
                runner = parse_runner_line(settings['runner'])
                try:
                    runner(msg_body, set_status, settings)
                except Exception, err:
                    # Grab all Exceptions
                    set_status('Failed', err)
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

        self._connection = pika.BlockingConnection(connection_parameters)
        self._channel = self._connection.channel()

        for suite, info in self._queue_list.iteritems():
            queue = info['queue']
            route = info['route']
            logging.debug("Creating queue with name:" + queue)
            self._channel.queue_declare(queue=queue,
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


def main(argv=None):
    """Command line utility"""
    parser = argparse.ArgumentParser(description="PyBit builder for rhaptos")
    parser.add_argument('--poll-time', type=int, default=60,
                        help="time to poll between idle periods")
    parser.add_argument('config', type=argparse.FileType('r'),
                        help="INI configuration file")
    args = parser.parse_args(argv)

    # Load the configuration
    config = Config.from_file(args.config)
    # Create the client
    client = Client.from_config(config)

    # Roll through the client at a time interval.
    while True:
        time.sleep(args.poll_time)
        client.act()


if __name__ == '__main__':
    main()
