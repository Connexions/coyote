Coyote
======

Coyote is a generalized consumer implemenation that communicates with
RabbitMQ to do various pieces of work that have been put there by the
transformations services (`acmeio <https://github.com/Connexions/acmeio>`_)
API and status system.

Getting Started
---------------

This code uses ``setuptools`` to distribute itself. To install, use
one of the following methods::

    $ python setup.py install

Using ``pip`` you can install a released version, like so::

    $ pip install coyote

Or, the development version by pointing pip at the checked out
directory, like so::

    $ pip install $CHECKOUT_LOCATION/rbit/


Coyote Logic Overview
---------------------

There are three parts of to this application:

1. The client implementation, which can be invoked and/or daemonized
   via the commandline interface (CLI). This piece of code is used by the
   system/user to read and execute configured job runners.

2. The job logic (also known as the *runner*) is linked to
   a callable that adheres to a specific parameter interface.
   This logic is made available through the configuration mapping of
   the queue name to the callable in the client component of this
   application.

3. A configuration file supplies the CLI utility with mappings to
   runners and it also supplies settings/configuration to the runners
   themeselves.

Usage
-----

The general usage of the code from the command line interface (CLI)
goes as follows::

    $ coyote plans.ini

In this case we are telling the ``coyote`` CLI utility setup itself
using the ``plans.ini`` file, which contains information about message
queue connections and runner definitions.

And the fun explanation of this... The ``coyote`` lays reads his/her
plans and waits for a shipment from acme. Once the shipment is
recieved ``coyote`` sets up the process and lays out the bird seed. The
road runner quickly comes along and does it's duty. :)

Also, the ``coyote`` interface will happily run in foreground mode until you
decide to stop the process using ``Ctrl+c``.

Configuration
-------------

The configuration is stored in an INI format for simplicity. There are
**two required sections**: ``coyote`` and ``amqp``. They
contain settings for the client itself and the message queue,
respectfully. All sections prefixed with `runner:` are
considered job runner definitions. For example::

    [coyote]
    queue-mappings =
        cnx_desktop_latex_pdf:legacy-print
        cnx_desktop_latex_offline:offlinezip    

    [amqp]
    host = localhost
    port = 5672
    user = guest
    password = guest

    ...

The ``queue-mappings`` setting is a new line indented or space
separated list of mappings, which contain the queue name and runner
name separated by a colon (``:``).

A runner can be named whatever, as long as it does not contain
spaces. A runner definition is an INI section prefixed with
``runner:``. For example::

    [runner:legacy-print]
    runner = python!geriatric_roadrunners:make_print

Each job runner can have it's own settings. For a
section to be a valid runner it **must** define a value for the
``runner`` setting in the job runner's section. This value points to
the callable that will handle the queued message.

.. note:: The syntax for the runner value is,
   ``<processor-name>!<processor-specific-arguments>``. For example,
   the ``python`` processor accepts the ``<module-path>:<callable>``.

Runner Implementation
---------------------

.. attention:: This runner interface will change in the near
   future. The change will take place when PyBit is factored out
   ``acmeio``.

A job runner is a callable used to carry out the work.
The runner is defined in configuration by the processor, which calls
the actually working logic or is the working logic itself. For
example, you might configure a shell process like this::

    [runner:html2pdf]
    runner = shell!html2pdf %ID.pdf

Or a Python runner like::

    [runner:legacy-print]
    runner = python!geriatric_roadrunners:make_print
    python = /usr/local/bin/python2.4
    print-dir = Products.RhaptosPrint/Products/RhaptosPrint/printing
    output-dir = /var/pdfs

The Python processor executes a callable (e.g. function).
The callable is given the build request object and runner settings are
parameters. Anything was written to the filesystem should be returned
in as a list item that points to the absolute location.

Here is a very simple hello world example of a job runner function in
the ``my_worker.py`` module.
::

    def hello(build_request, settings={}):
        try:
            print("Hello {0}!".format(settings['name']))
        except KeyError, err:
            raise coyote.Failed("A 'name' was not configured.")
        print("Building {0}".format(build_request.get_package()))
        return []

And the INI formated configuration for this::

    [runner:hello]
    runner = python!my_worker:hello
    name = World

Note the use of ``coyote.Failed``. There are two types of exceptions
used to report back a problem state: ``coyote.Failed`` and
``coyote.Blocked``. As seen here, the Failed exception is used to report
on a known error that can't be recovered from. The Blocked exception
on the other hand is used to gracefully fail, but re-queue the job. It
is typically used in situations where an external input isn't
available yet.

License
-------

This software is subject to the provisions of the GNU Affero General
Public License Version 3.0 (AGPL). See license.txt for details.
Copyright (c) 2013 Rice University
