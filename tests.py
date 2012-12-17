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
MOCK_QUEUE_MESSAGE = (None, None, '{"py/object": "pybit.models.BuildRequest", "commands": "", "timestamp": null, "job": {"py/object": "pybit.models.Job", "packageinstance": {"py/object": "pybit.models.PackageInstance", "format": {"py/object": "pybit.models.Format", "id": 1, "name": "completezip"}, "package": {"py/object": "pybit.models.Package", "version": "1.2", "id": 1, "name": "m9003"}, "master": false, "suite": {"py/object": "pybit.models.Suite", "id": 1, "name": "latex"}, "distribution": {"py/object": "pybit.models.Dist", "id": 3, "name": "openstax"}, "arch": {"py/object": "pybit.models.Arch", "id": 1, "name": "any"}, "id": 1}, "id": 1, "buildclient": null}, "transport": {"py/object": "pybit.models.Transport", "uri": "http://cnx.org/content/", "id": null, "vcs_id": "latest", "method": "http"}, "web_host": "localhost:8080"}',)
TEST_QUEUE_NAME = 'openstax_any_latex_completezip'


def test_runner_info_getter(message, set_status, settings={}):
    """Get some info and stick it in the settings."""
    # Push the current location into the settings for a simple check
    set_status('Building', "Gathering build information.")
    build_request = jsonpickle.decode(message)
    settings['package_url'] = None
    settings['here'] = here
    set_status('Done', "Work complete, values stored...")

def test_runner_process_w_failure(message, set_status, settings={}):
    """Do some work."""
    set_status('Building', "Making assertions")
    assert 'here' in settings
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

    def test_no_connection_error(self):
        # Make sure the NotConnectedError is raised when a connection
        #   hasn't been initialized.
        from rbit import Config
        config = Config.from_file(TESTING_CONFIG)
        from rbit import Client
        client = Client.from_config(config)
        from rbit import NotConnectedError
        with self.assertRaises(NotConnectedError):
            client.act()


class ClientTest(unittest.TestCase):

    def _make_config(self):
        from rbit import Config
        return Config.from_file(TESTING_CONFIG)

    def _make_one(self, config=None):
        if config is None:
            config = self._make_config()
        from rbit import Client
        client = Client.from_config(config)
        self._patch_client_channel(client)
        return client

    def _patch_client_channel(self, client):
        # Patch the client's connection code.
        client._channel = mock.MagicMock()
        client._channel.basic_get.return_value = MOCK_QUEUE_MESSAGE

    def test_act_on_a_job(self):
        # Check for the intented results.
        client = self._make_one()
        client.act()
        # Check to see if the runer appended to the runner settings
        runner_settings = client._runner_settings[TEST_QUEUE_NAME]
        self.assertIn('here', runner_settings)
        self.assertEqual(runner_settings['here'], here)

    def test_set_status_on_failure(self):
        # Check for status results.
        config = self._make_config()
        # Override the config to use a failing pipeline. Without the
        #   first pipeline function, the main endpoint will fail due
        #   to the missing setting.
        runner_line = 'python!tests:test_runner_process_w_failure'
        config._runners[TEST_QUEUE_NAME]['runner'] = runner_line

        # Patch the _set_status method to capture the messages.
        statuses = []
        def _set_status(status, build_request):
            statuses.append(status)

        client = self._make_one(config)
        client._set_status = _set_status

        client.act()
        self.assertTrue(len(statuses) == 2)  # ['Building', 'Failed']
        self.assertEqual(statuses[1], 'Failed')
