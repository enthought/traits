#------------------------------------------------------------------------------
#
#  Copyright (c) 2013, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in enthought/LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!
#
#  Author: Simon Jagoe
#
#------------------------------------------------------------------------------
""" Debugging helpers to record trait change events in single and
multi-threaded environments.

"""
from contextlib import contextmanager
import inspect
import os
import sys
import threading
from datetime import datetime

from traits import trait_notifiers


CHANGEMSG = (
    u"{time} {direction:-{direction}{length}} '{name}' changed from "
    u"{old} to {new} in '{class_name}'\n")
CALLINGMSG = u"{time} {action:>{gap}}: '{handler}' in {source}\n"
EXITMSG = (
    u"{time} {direction:-{direction}{length}} "
    u"EXIT: '{handler}'{exception}\n")


class BaseMessageEventRecord(object):

    __slots__ = ()

    def __init__(self, **kwargs):
        for attr, value in kwargs.iteritems():
            setattr(self, attr, value)

    def __unicode__(self):
        return u'\n'

class ChangeMessageEventRecord(BaseMessageEventRecord):

    __slots__ = ('time', 'direction', 'indent', 'name', 'old', 'new',
                 'class_name')

    def __unicode__(self):
        length = self.indent * 2
        return CHANGEMSG.format(
            time=self.time,
            direction=self.direction,
            name=self.name,
            old=self.old,
            new=self.new,
            class_name=self.class_name,
            length=length,
        )


class CallingMessageEventRecord(BaseMessageEventRecord):

    __slots__ = ('time', 'indent', 'action', 'handler', 'source')

    def __unicode__(self):
        gap = self.indent * 2 + 9
        return CALLINGMSG.format(
            time=self.time,
            action=self.action,
            handler=self.handler,
            source=self.source,
            gap=gap
        )


class ExitMessageEventRecord(BaseMessageEventRecord):

    __slots__ = ('time', 'direction', 'indent', 'handler', 'exception')

    def __unicode__(self):
        length = self.indent * 2
        return EXITMSG.format(
            time=self.time,
            direction=self.direction,
            handler=self.handler,
            exception=self.exception,
            length=length,
        )


class ThreadChangeEventContainer(object):

    def __init__(self):
        self._records = []

    def record(self, record):
        self._records.append(record)

    def save_to_file(self, filename):
        with open(filename, 'w') as fh:
            for record in self._records:
                fh.write(unicode(record))


class ChangeEventContainer(object):

    def __init__(self):
        self._change_event_containers_lock = threading.Lock()
        self._thread_change_event_containers = {}

    def get_change_event_collector(self, thread_name):
        with self._change_event_containers_lock:
            container = self._thread_change_event_containers.get(thread_name)
            if container is None:
                container = ThreadChangeEventContainer()
                self._thread_change_event_containers[thread_name] = container
            return container

    def save_to_directory(self, directory_name):
        with self._change_event_containers_lock:
            containers = self._thread_change_event_containers
            for thread_name, container in containers.iteritems():
                filename = os.path.join(
                    directory_name, '{0}.trace'.format(thread_name))
                container.save_to_file(filename)


class ChangeEventRecorder(object):
    """ A thread aware trait change recorder

    The class manages multiple ThreadChangeEventRecorders which record
    trait change events for each thread in a separate file.

    """

    def __init__(self, change_event_container):
        """ Object constructor

        Parameters
        ----------
        trace_directory : string
            The directory where the change log for each thread will be saved

        """
        self.tracers = {}
        self.tracer_lock = threading.Lock()
        self.change_event_container = change_event_container

    def close(self):
        """ Close log files.

        """
        with self.tracer_lock:
            self.tracers = {}

    def pre_tracer(self, obj, name, old, new, handler):
        """ The traits pre event tracer.

        This method should be set as the global pre event tracer for traits.

        """
        tracer = self._get_tracer()
        tracer.pre_tracer(obj, name, old, new, handler)

    def post_tracer(self, obj, name, old, new, handler, exception=None):
        """ The traits post event tracer.

        This method should be set as the global post event tracer for traits.

        """
        tracer = self._get_tracer()
        tracer.post_tracer(obj, name, old, new, handler, exception=exception)

    def _get_tracer(self):
        with self.tracer_lock:
            thread = threading.current_thread().name
            if thread not in self.tracers:
                container = self.change_event_container
                thread_container = container.get_change_event_collector(thread)
                tracer = ThreadChangeEventRecorder(thread_container)
                self.tracers[thread] = tracer
                return tracer
            else:
                return self.tracers[thread]


class ThreadChangeEventRecorder(object):
    """ A single thread trait change event recorder.

    """

    def __init__(self, change_event_container):
        """ Class constructor

        Parameters
        ----------
        fh : stream
           An io stream to store the records for each trait change.

        """
        self.indent = 1
        self.change_event_container = change_event_container

    def pre_tracer(self, obj, name, old, new, handler):
        """ Record a string representation of the trait change dispatch

        """
        indent = self.indent
        time = datetime.utcnow().isoformat(' ')
        container = self.change_event_container
        container.record(
            ChangeMessageEventRecord(
                time=time,
                direction='>',
                indent=indent,
                name=name,
                old=old,
                new=new,
                class_name=obj.__class__.__name__,
            ),
        )

        container.record(
            CallingMessageEventRecord(
                time=time,
                indent=indent,
                action='CALLING',
                handler=handler.__name__,
                source=inspect.getsourcefile(handler),
            ),
        )
        self.indent += 1

    def post_tracer(self, obj, name, old, new, handler, exception=None):
        """ Record a string representation of the trait change return

        """
        time = datetime.utcnow().isoformat(' ')
        self.indent -= 1
        indent = self.indent
        if exception:
            exception_msg = ' [EXCEPTION: {}]'.format(exception)
        else:
            exception_msg = ''

        container = self.change_event_container

        container.record(
            ExitMessageEventRecord(
                time=time,
                direction='<',
                indent=indent,
                handler=handler.__name__,
                exception=exception_msg,
            ),
        )

        if indent == 1:
            container.record(BaseMessageEventRecord())


@contextmanager
def record_events():
    """ Multi-threaded trait change event tracer.

    Parameters
    ----------
    trace_directory : string
        The directory where the change log for each event will be saved

    Usage
    -----
    ::

        >>> from trace_recorder import record_events
        >>> with record_events() as change_event_container:
        ...     my_model.some_trait = True
        >>> change_event_container.save_to_directory('C:\\dev\\trace')

    This will install a tracer that will record all events that occur from
    setting of some_trait on the my_model instance.

    The results will be stored in one file per running thread in the
    directory 'C:\\dev\\trace'.  The files are named after the thread being
    traced.

    """
    container = ChangeEventContainer()
    recorder = ChangeEventRecorder(container)
    trait_notifiers.set_change_event_tracers(
        pre_tracer=recorder.pre_tracer, post_tracer=recorder.post_tracer)

    try:
        yield container
    finally:
        trait_notifiers.clear_change_event_tracers()
        recorder.close()
