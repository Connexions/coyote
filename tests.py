# -*- coding: utf-8 -*-
"""Functional tests for the `rbit`` implementation.

DO NOT have a production (rabbitmq) message queue running while running these
tests, because it will destroy the live data.
Thank you for you co-opperation. =)

"""
import os
import unittest


here = os.path.abspath(os.path.dirname(__file__))
TESTING_CONFIG = os.path.join(here, 'testing.ini')


class ClientConfigurationTest(unittest.TestCase):

    def test_client_init_from_config(self):
        # Test the client can be initialized from a configuration
        #   object.
        from rbit import Config
        config = Config.from_file(TESTING_CONFIG)
        from rbit import Client
        client = Client.from_config(config)
        # We'll assume the setting were set correctly. If they
        #   weren't... well, stuff won't work.
        # This is more of a check that the class method can create an
        #   Client instance.
        self.assertTrue(isinstance(client, Client))


class ClientBaseFunctionalityTest(unittest.TestCase):

    def test_connecting_and_disconnecting(self):
        # This is mostly a smoke test to check for common errors.
        from rbit import Client
        ##client = Client()
