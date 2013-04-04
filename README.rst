.. Michael Mulich, Copyright (c) 2012 Rice University

   This software is subject to the provisions of the GNU Lesser General
   Public License Version 2.1 (LGPL).  See LICENSE.txt for details.

Rhaptos PyBit Client
====================

A client implemenation that communicates with RabbitMQ to do various
pieces of work. For example, the transformation of a module from HTML
to EPUB is a process that can take a considerable amount of time. This
implementation allows for the ability to do the work outside the scope
of the user front-end.

Client Logic Overview
---------------------

The client code is broken up into three parts. The first part is the
client implementation, which can be trigger/controlled/daemonized on
the command line interface. This piece of code is used by the
system/user to execute the jobs in the queuing system.

The second part is the job logic. This differs based on what kind of
work needs to be done. However, it does adhere to a set interface. The
logic is configured via a job runner or simply runner(python function).

The third and final part of the client code allows for the client user
or system admin to set up the client using a (set of) configuration
file(s). The configuration contains information about PyBit
Web application (This will be removed at some point, because we don't want
the client code to depend on the web front-end.), the message queue,
and the job runner.

Usage
-----

The general usage of the code from the command line interface goes as follows::

    $ rbit rbit.ini

In this case we are telling the `rbit` interface to start in debug
mode, which allows for more information to be printed to standard
out. The single file argument is the configuration file containing
general information about the message queue as well as the configured
runners.

The command line interface accepts a ``--poll-time`` option with a
value in seconds. The default value for this option is ``60``. This
option controls how often the client will check the message queue
for new messages.

The `rbit` interface will happily run in foreground more until you
decide to stop the process using `Ctrl+c`.

Configuration
-------------

The configuration is stored in an ini format for simplicity. There are
**two required sections**. They are `rbit` and `amqp`,
which contain settings for the client itself and the message queue,
respectfully. All sections prefixed with `runner:` are/will be
considered job runner definitions. For example::

    [rbit]
    # The `name` corresponds with the `BuildBox` registration in PyBit's
    #   web interface.
    name = bob-villa
    polling_time = 60
    architecture = any
    distribution = cnx
    format = princexml
    # The `suites` is a list of suites separated by commas (,).
    suites = latex, princexml
    
    [amqp]
    host = localhost
    port = 5672
    user = guest
    password = guest

At this time, job runner(s) are named by distribution, architecture,
suite and format (e.g. cnx_any_princexml_epub). These runner names
directly correspond with the queue names. This is primarily because I
don't know of a better way to name them at this time.

.. note:: The way naming of runners will likely change in some iteration.

Each job runner can have it's own set of configuration values. For a
section to be a valid runner it **must** define a value for the
`runner` attribute in the job runner's section. For example::

    [runner:openstax_any_latex_pdf]
    runner = python!Products.RhaptosPrint.printing:main
    deposit_location = /mnt/www

Job Runner
----------

A job runner is a piece of logic used to carry out the work
The runner is defined in configuration by the processor, which calls
the actually working logic or is the working logic itself. For
example, you might configure a shell process like this::

    [runner:cnx_desktop_princexml_epub]
    runner = shell!%ID.pdf

Or a Python runner like::

    [runner:cnx_any_latex_pdf]
    runner = python!rbitext.rhaptos_print:make_print
    python = /usr/local/bin/python2.4
    print-dir = Products.RhaptosPrint/Products/RhaptosPrint/printing
    host = http://cnx.org

The Python processor calls a function. The function is given access to
the message body, a status callback function and the locally defined
configuration settings. The status callback function can be used one
or more times during the process. It is the job of the logic to update
the status of the job as work is being done. However, if an unknown
exception occures, the client will report the failure iteself.

Here is a very simple hello world example of job runner function in
the ``my_worker.py`` module.
::

    def hello(message, set_status, settings={}):
        status_message = "Starting job at {0}".format(datetime.now())
        set_status('Building', status_message)
        build_request = jsonpickle.decode(message.body)

        # Do some work
        try:
            print("Hello {0}!".format(settings['name']))
        except KeyError, err:
            set_status('Failed', err)
            return

        print("Building {0}".format(build_request.get_package()))

        status_message = "Completed job at {0}".format(datetime.now())
        set_status('Done', status_message)

The configuration for this might look like this::

    [runner:ccap_any_latex_completezip]
    runner = python!my_worker:hello
    name = World

In this example, we set the status twice. We set the status during the
start of the job. Then we may or maynot set the status to failed due
to a missing setting. And finally, if the job is successful, set the
status to done.

Why decode the message in the job? Why not pass in the BuildRequest
object instead of the raw message? Sending in the raw data is better
because if we later want to change the interface, we don't have to
change the variable naming and/or behavior.

The statuses used are those used in the PyBit web front-end. (How the
callback gets information there is to be determined at implementation
time.)

Installation and Tests
----------------------

Installation
~~~~~~~~~~~~

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

Testing
~~~~~~~

The only way to run the tests for this distribution are to unpack the
distribution contents manually. We purposely do not install the tests
with the package. If you were to run the tests on a production
system, you could bork the live data in your message queue.

To run the tests, change into the distribution root and run the
``unittest`` discovery command on from there::

    $ cd $DISTRIBUTION_ROOT
    $ python -m unittest discover

Reverse Engineering PyBit Client
--------------------------------

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
front-end. However, chances are that it would only disable the
filtering of job status results.

The 'Blocked' status is something we will likely not use in the near
future. The PyBit client implemenation uses this status in one
place. It is used when a build fails due to missing dependencies,
in which case the client sets the status to blocked.
As a result the job gets republished to the queue.

PyBit Queue Design
~~~~~~~~~~~~~~~~~~

The queues used by PyBit are named queues with named routes. It looks
to me that the contents that the queue and the route have the same
names. This doesn't really help anything and in fact is a bit
redundant. I believe the PyBit developers have taken this approach
for one of two reasons:

1. Creating a named queue from the PyBit web front-end allows for the
   job to be sent to a queue no matter the status of the queues,
   because without setting up the queus in the web front-end there
   would be nowhere to send the job.
2. They may have started with named queues and never got the chance to
   remove the implementation.

I think the best approach in this situation would be to setup a named
queue from the PyBit web front-end that recieves all messages. Then
have a default listener that watches for new build-clients. Once it
sees a new build client it cycles through the queue, republishing
queued items that have been put in the default queue.

This approach could be taken a step further to stop and start workers
based on work available and the usage of slave boxes.

License
-------

This software is subject to the provisions of the GNU Affero General Public License Version 3.0 (AGPL). See license.txt for details. Copyright (c) 2012 Rice University
