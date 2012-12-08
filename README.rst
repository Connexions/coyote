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

The third and final part of the clien code allows for the client user
or system admin to set up the client using a (set of) configuration
file(s). The configuration contains information about PyBit
Web application (This will be removed at some point, because we don't want
the client code to depend on the web front-end.), the message queue,
and the various pipelines.
