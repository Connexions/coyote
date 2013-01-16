# -*- coding: utf-8 -*-
"""\
Pybit producer of jobs. This is mostly to be used in testing.

Author: Michael Mulich
Copyright (c) 2012 Rice University

Parts of the client code are derived from the PyBit client implementation at
https://github.com/nicholasdavidson/pybit licensed under GPL2.1.

This software is subject to the provisions of the GNU Lesser General
Public License Version 2.1 (LGPL).  See LICENSE.txt for details.
"""
import argparse
import requests


def push_package(args):
    """Adds a package to PyBit"""
    url = "http://{0}:{1}/package/".format(args.host, args.port)
    auth = (args.user, args.password,)
    data = {'name': args.id, 'version': args.version}
    resp = requests.post(url, data=data, auth=auth)
    if resp.status_code != 200:
        return -1
    return 0


def main(argv=None):
    """Command line utility"""
    parser = argparse.ArgumentParser(description="PyBit builder for rhaptos")
    parser.add_argument('--host', default='localhost',
                        help="PyBit web frontend hostname")
    parser.add_argument('--port', type=int, default=8080,
                        help="Port that the PyBit frontend runs on")
    parser.add_argument('--user', default='admin',
                        help="Username for auth against PyBit")
    parser.add_argument('--password', default='pass',
                        help="password for auth against PyBit")
    # Subcommands: package, instance, and job
    subparsers = parser.add_subparsers()
    package_parser = subparsers.add_parser('package',
                                           help="adds a module/collection")
    instance_parser = subparsers.add_parser('instance',
                                            help="adds a module/collection "\
                                                 "instance")
    job_parser = subparsers.add_parser('job',
                                       help="adds a job to build a "\
                                            "module/collection")
    package_parser.add_argument('id', help="module/collection id")
    package_parser.add_argument('version',
                                help="version of the module/collection")
    package_parser.set_defaults(func=push_package)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == '__main__':
    main()
