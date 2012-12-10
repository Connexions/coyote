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


def test_pipeline_info_getter(message, set_status, settings):
    """Get some info and stick it in the settings."""
    # Push the current location into the settings for a simple check
    set_status('Building', "Gathering build information.")
    settings['here'] = here

def test_pipeline_process_info(message, set_status, settings):
    """Do some work."""
    try:
        assert 'here' in settings
    except AssertionError, err:
        set_status('Failed', err)
        raise err
    # The work... Note: The results of the work wouldn't normally be
    #   stored in the settings, but this is the easiest way to test
    #   for job completion.
    settings['value'] = message
    set_status('Done', "Work complete, value stored...")


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

    # XXX This is a test that can be removed. It is a preliminary test
    #     to verify a connection can be made.
    def test_connecting_and_disconnecting(self):
        # This is mostly a smoke test to check for common errors.
        from rbit import Config
        config = Config.from_file(TESTING_CONFIG)
        from rbit import Client
        client = Client.from_config(config)
        with client as connected_client:
            connected_client.act()
        # If the connection is good this test passes.
