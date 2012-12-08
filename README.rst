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
    package_format = princexml
    # The `suites` is a list of suites separated by commas (,).
    suites = latex, princexml
    
    [mq]
    host = localhost
    port = 5432
    user = guest
    password = guest

Each pipeline can have it's own set of configuration values. For a
section to be a valid pipeline it **must** define a value for the
`pipeline` attribute in the pipeline's section. For example::

    [pdf]
    pipeline:
        python!rbit.ext.pdf:gimmie_info
        python!Products.RhaptosPrint.printing:main
        shell!cp module.pdf {settings.deposit_location}/
    deposit_location = /mnt/www

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
