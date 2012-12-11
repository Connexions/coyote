# -*- coding: utf-8 -*-
"""Functional tests for the `rbit`` implementation.

DO NOT have a production (rabbitmq) message queue running while running these
tests, because it will destroy the live data.
Thank you for you co-opperation. =)

"""
import os
import unittest

import mock

import jsonpickle
import pybit


here = os.path.abspath(os.path.dirname(__file__))
TESTING_CONFIG = os.path.join(here, 'testing.ini')


def test_pipeline_info_getter(message, set_status, settings):
    """Get some info and stick it in the settings."""
    # Push the current location into the settings for a simple check
    set_status('Building', "Gathering build information.")
    build_request = jsonpickle.decode(message)
    settings['package_url'] = None
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


class XXXClientBaseFunctionalityTest(unittest.TestCase):

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


class ClientTest(unittest.TestCase):

    def _make_config(self):
        from rbit import Config
        return Config.from_file(TESTING_CONFIG)

    def test_act_on_a_job(self):
        # Create a job, act on it and check for the intented results.

        from rbit import Client
        client = Client.from_config(self._make_config())
        # Patch the client's connection code.
        client._channel = mock.MagicMock()
        client._channel.basic_get.return_value = (None, None, '{"py/object": "pybit.models.BuildRequest", "commands": "", "timestamp": null, "job": {"py/object": "pybit.models.Job", "packageinstance": {"py/object": "pybit.models.PackageInstance", "format": {"py/object": "pybit.models.Format", "id": 1, "name": "completezip"}, "package": {"py/object": "pybit.models.Package", "version": "1.2", "id": 1, "name": "m9003"}, "master": false, "suite": {"py/object": "pybit.models.Suite", "id": 1, "name": "latex"}, "distribution": {"py/object": "pybit.models.Dist", "id": 3, "name": "openstax"}, "arch": {"py/object": "pybit.models.Arch", "id": 1, "name": "any"}, "id": 1}, "id": 1, "buildclient": null}, "transport": {"py/object": "pybit.models.Transport", "uri": "http://cnx.org/content/", "id": null, "vcs_id": "latest", "method": "http"}, "web_host": "localhost:8080"}',)
        client.act()
