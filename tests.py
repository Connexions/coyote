# -*- coding: utf-8 -*-
"""Functional tests for the `rbit`` implementation.

DO NOT have a production (rabbitmq) message queue running while running these
tests, because it will destroy the live data.
Thank you for you co-opperation. =)

"""
import os
import unittest


class ClientBaseFunctionalityTest(unittest.TestCase):

    def test_connecting_and_disconnecting(self):
        # This is mostly a smoke test to check for common errors.
        from rbit import Client
        ##client = Client()
