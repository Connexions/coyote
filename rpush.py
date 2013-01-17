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
import sys
import argparse
import requests


def add_package(args):
    """Adds a package to PyBit"""
    url = "http://{0}:{1}/package/".format(args.host, args.port)
    auth = (args.user, args.password,)
    data = {'name': args.id, 'version': args.version}
    resp = requests.post(url, data=data, auth=auth)
    if resp.status_code != 200:
        raise Exception("Failed to add the package with the following data:"
                        "\ndata: {0}"
                        "\nresponse status: {1}"
                        "\nresponse body: {2}"
                        .format(data, resp.status_code, resp.text))


def _name2id(lookup_name, name, args):
    """Map the lookup name to an id"""
    url = "http://{0}:{1}/{2}/page/1".format(args.host, args.port, lookup_name)
    auth = (args.user, args.password,)
    resp = requests.get(url, auth=auth)
    data = dict([(v['name'], v['id'],) for v in resp.json])
    return data[name]


def add_instance(args):
    """Adds a package instance to PyBit"""
    url = "http://{0}:{1}/packageinstance/".format(args.host, args.port)
    auth = (args.user, args.password,)
    data = {'package': args.id,
            'version': args.version,
            'arch_id': _name2id('arch', args.platform, args),
            'suite_id': _name2id('suite', args.suite, args),
            'dist_id': _name2id('dist', args.project, args),
            'format_id': _name2id('format', args.format, args),
            }
    resp = requests.post(url, data=data, auth=auth)
    if resp.status_code != 200:
        raise Exception("Failed to add the package with the following data:"
                        "\ndata: {0}"
                        "\nresponse status: {1}"
                        "\nresponse body: {2}"
                        .format(data, resp.status_code, resp.text))


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
    package_parser.set_defaults(func=add_package)
    package_parser.add_argument('id', help="module/collection id")
    package_parser.add_argument('version',
                                help="version of the module/collection")

    instance_parser = subparsers.add_parser('instance',
                                            help="adds a module/collection "\
                                                "instance")
    instance_parser.set_defaults(func=add_instance)
    instance_parser.add_argument('id', help="module/collection id")
    instance_parser.add_argument('version',
                                 help="version of the module/collection")
    instance_parser.add_argument('--platform', default='any',
                                 help="platform to build for, default is any")
    instance_parser.add_argument('--suite', default='latex',
                                 help="build suite to use, default is latex")
    instance_parser.add_argument('--project', default='cnx',
                                 help="build for a specific project, default "\
                                      "is cnx")
    instance_parser.add_argument('--format', default='pdf',
                                 help="build format, default is pdf")

    job_parser = subparsers.add_parser('job',
                                       help="adds a job to build a "\
                                           "module/collection")

    args = parser.parse_args(argv)
    args.func(args)


if __name__ == '__main__':
    main()
