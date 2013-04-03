.. Michael Mulich, Copyright (c) 2012 Rice University

   This software is subject to the provisions of the GNU Lesser General
   Public License Version 2.1 (LGPL).  See LICENSE.txt for details.

rbit
====

rbit is pronounced 'R-bit', but with a slight hint that could roughly
be pronouced 'Ri-bit'.

rbit is a generalized consumer implemenation that communicates with
RabbitMQ to do various pieces of work that have been put their by the
PyBit status system.

rbit Logic Overview
-------------------

The code is broken up into three parts. The first part is the
client implementation, which can be trigger/controlled/daemonized on
the command line interface. This piece of code is used by the
system/user to execute the jobs in the queuing system.

The second part is the job logic (also known as the *runner*)--this
differs based on what kind of work needs to be done--is linked to
a callable that adheres to a specific parameter interface.
This logic is made available through
the configuration mapping of the queue name to the callable.

The third and final part of the code allows for the client user
or system admin to set up the client using a configuration
file. The configuration contains information about the PyBit
Web application (This will be removed at some point, because we don't want
the code to depend on the web front-end.), the message queue,
and the queue to runner mappings as well as any runner specific settings.

Usage
-----

The general usage of the code from the command line interface goes as follows::

    $ rbit rbit.ini

In this case we are telling the `rbit` command-line script to invoke
the runners. The single file argument is the configuration file containing
general information about the message queue as well as the configured
runners.

The ``rbit`` interface will happily run in foreground mode until you
decide to stop the process using ``Ctrl+c``.

Configuration
-------------

The configuration is stored in an INI format for simplicity. There are
**two required sections**: ``rbit`` and ``amqp``. They
contain settings for the client itself and the message queue,
respectfully. All sections prefixed with `runner:` are
considered job runner definitions. For example::

    [rbit]
    # The `name` corresponds with the `BuildBox` registration in PyBit's
    #   web interface.
    name = bob-villa
    # These queue to runner mappings (<queue_name>:<runner_name>) propulate the
    #   queues list to run through during runtime.
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
    runner = python!rbit.legacy:make_print

Each job runner can have it's own set of settings. For a
section to be a valid runner it **must** define a value for the
``runner`` setting in the job runner's section. This value points to
the callable that will handle the queued
message.

.. note:: The syntax for the runner value is,
   ``<processor-name>!<processor-specific-arguments>``. For example,
   the ``python`` processor accepts the ``<module-path>:<callable>``.

Runner Implementation
---------------------

A job runner is a callable used to carry out the work.
The runner is defined in configuration by the processor, which calls
the actually working logic or is the working logic itself. For
example, you might configure a shell process like this::

    [runner:html2pdf]
    runner = shell!html2pdf %ID.pdf

Or a Python runner like::

    [runner:legacy-print]
    runner = python!rbitext.legacy:make_print
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
            raise rbit.Failed("A 'name' was not configured.")
        print("Building {0}".format(build_request.get_package()))
        return []

And the INI formated configuration for this::

    [runner:hello]
    runner = python!my_worker:hello
    name = World

Note the use of ``rbit.Failed``. There are two types of exceptions
used to report back a problem state: ``rbit.Failed`` and
``rbit.Blocked``. As seen here, the Failed exception is used to report
on a known error that can't be recovered from. The Blocked exception
on the other hand is used to gracefully fail, but re-queue the job. It
is typically used in situations where an external input isn't
available yet.

.. The status names are those defined in the PyBit web front-end. (How the
   callback gets information about the names is to be determined
   at implementation time.)

Installation
------------

This code uses ``setuptools`` to distribute itself. To install, use of
the following methods::

    $ python setup.py install

The following will to obtain released versions::

    $ easy_install rbit

Using `pip` you can install a released version, like so::

    $ pip install rbit

Or, the development version by pointing pip at the checked out
directory, like so::

    $ pip install $CHECKOUT_LOCATION/rbit/

Reverse Engineering PyBit Client
--------------------------------

This part of the readme contains information about 

The implementation of PyBit client is specific to the Debian package
build process. The code is setup to use a number of state handlers,
which are triggered in (I think) a specific order. The handlers are
small chuncks of logic that can be analyzed after run completion,
which enables the client to update the status of the build in the
PyBit web front-end.

PyBit Statuses
~~~~~~~~~~~~~~

The implementation of statuses in PyBit seems incomplete at this
time. The code that is used in PyBit Client has a static set of
statuses to pull from. At the same time, the web front-end allows for
the creation and deletion of statuses. This makes sense, but could
result in odd behavior if the statuses are removed from the
front-end. Removal would likely only disable the filtering of job
results by status.

PyBit Queue Design
~~~~~~~~~~~~~~~~~~

The queues used by PyBit are named queues with named routes.
I believe the PyBit developers have taken a named queue approach
for one of two reasons:

1. Using named queues allows the producer to create queues where it
   knowns data will persist even if no consumer is listening. 
2. They may have started with named queues and never got the chance to
   remove the implementation.
