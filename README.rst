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
logic is configured via a pipeline (python list). The pipeline can
consist of one or more executable tasks. A state object is given to
each member of the pipeline, which can be used to pass along work done
in the previous pipeline step. Upon completion of the pipeline, the
state object can be used to infer complete or partial success.

The third and final part of the client code allows for the client user
or system admin to set up the client using a (set of) configuration
file(s). The configuration contains information about PyBit
Web application (This will be removed at some point, because we don't want
the client code to depend on the web front-end.), the message queue,
and the various pipelines.

Usage
-----

The general usage of the code from the command line interface goes as follows::

    $ rbit --debug rbit.ini

In this case we are telling the `rbit` interface to start in debug
mode, which allows for more information to be printed to standard
out. The single file argument is the configuration file containing
general information about the message queue as well as the configured
pipelines.

The `rbit` interface will happily run in foreground more until you
decide to stop the process using `Ctrl+c`.

Configuration
-------------

The configuration is stored in an ini format for simplicity. There are
**two required sections**. They are `rbit` and `mq`,
which contain settings for the client itself and the message queue,
respectfully. All other sections are/will be considered pipeline
definitions. For example::

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
    port = 5432
    user = guest
    password = guest

At this time, pipelines are named by distribution, architecture,
suite and format (e.g. cnx_any_princexml_epub). These pipeline names
directly correspond with the queue names. This is primarily because I
don't know of a better way to name them at this time.

.. note:: The way naming of pipelines will likely change in some iteration.

Each pipeline can have it's own set of configuration values. For a
section to be a valid pipeline it **must** define a value for the
`pipeline` attribute in the pipeline's section. For example::

    [openstax_any_latex_pdf]
    pipeline:
        python!rbit.ext.pdf:gimmie_info
        python!Products.RhaptosPrint.printing:main
        shell!cp module.pdf {settings.deposit_location}/
    deposit_location = /mnt/www

Installation and Tests
----------------------

Installation
~~~~~~~~~~~~

This code uses `setuptools` to distribute itself. To install, use of
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
`unittest` discovery command on from there::

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
front-end. However, chances are that it would only disable job status
filtering results.

The 'Blocked' status is something we will likely not use in the near
future. The PyBit client implemenation uses this status in one
place. When a build fails due to missing dependencies, the client sets
the status to blocked. As a result the job gets republished/pushed
back onto the queue.

PyBit Queue Design
~~~~~~~~~~~~~~~~~~

The queues used by PyBit are named queues with named routes. It looks
to me that the contents that the queue and the route have the same
names. This doesn't really help anything and in fact is a bit
redundant. I believe they have taken this approach for one of two
reasons:

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
