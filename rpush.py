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
import json
import argparse
import requests


def create_job(args):
    """Creates a job in PyBit"""
    url = "http://{0}:{1}/api/job/".format(args.host, args.port)
    auth = (args.user, args.password,)
    data = {'package': args.id,
            'version': args.version,
            'uri': args.uri,
            'arch': args.platform,
            'dist': args.project,
            'suite': args.suite,
            'format': args.format,
            }
    data = json.dumps(data)
    headers = {'content-type': 'application/json'}
    resp = requests.post(url, data=data, auth=auth, headers=headers)
    if resp.status_code != 200:
        raise Exception("Failed to add the package with the following data:"
                        "\ndata: {0}"
                        "\nresponse status: {1}"
                        "\nresponse body: {2}"
                        .format(data, resp.status_code, resp.text))



def main(argv=None):
    """Command line utility"""
    parser = argparse.ArgumentParser(description="PyBit builder for rhaptos")

    # PyBit connection information
    parser.add_argument('--host', default='localhost',
                        help="PyBit web frontend hostname")
    parser.add_argument('--port', type=int, default=8080,
                        help="Port that the PyBit frontend runs on")
    parser.add_argument('--user', default='admin',
                        help="Username for auth against PyBit")
    parser.add_argument('--password', default='pass',
                        help="password for auth against PyBit")

    # Job information
    parser.add_argument('id', help="module/collection id")
    parser.add_argument('version',
                            help="version of the module/collection")
    parser.add_argument('uri', help="URI to the module/collection")
    parser.add_argument('--platform', default='any',
                        help="platform to build for, default is any")
    parser.add_argument('--suite', default='latex',
                        help="build suite to use, default is latex")
    parser.add_argument('--project', default='cnx',
                        help="build for a specific project, default is cnx")
    parser.add_argument('--format', default='pdf',
                        help="build format, default is pdf")

    args = parser.parse_args(argv)
    create_job(args)


if __name__ == '__main__':
    main()
