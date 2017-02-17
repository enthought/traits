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
#------------------------------------------------------------------------------
""" Record trait change events in single and multi-threaded environments.

"""
import inspect
import os
import threading
from contextlib import contextmanager
from datetime import datetime

from traits import trait_notifiers


CHANGEMSG = (
    u"{time} {direction:-{direction}{length}} {name!r} changed from "
    u"{old!r} to {new!r} in {class_name!r}\n")
CALLINGMSG = u"{time} {action:>{gap}}: {handler!r} in {source}\n"
EXITMSG = (
    u"{time} {direction:-{direction}{length}} "
    u"EXIT: {handler!r}{exception}\n")
SPACES_TO_ALIGN_WITH_CHANGE_MESSAGE = 9


class SentinelRecord(object):
    """ Sentinel record to separate groups of chained change event dispatches.

    """
    __slots__ = ()

    def __unicode__(self):
        return u'\n'


class ChangeMessageRecord(object):
    """ Message record for a change event dispatch.

    """

    __slots__ = ('time', 'indent', 'name', 'old', 'new', 'class_name')

    def __init__(self, time, indent, name, old, new, class_name):
        #: Time stamp in UTC.
        self.time = time
        #: Depth level in a chain of trait change dispatches.
        self.indent = indent
        #: The name of the trait that changed
        self.name = name
        #: The old value.
        self.old = old
        #: The new value.
        self.new = new
        #: The name of the class that the trait change took place.
        self.class_name = class_name

    def __unicode__(self):
        length = self.indent * 2
        return CHANGEMSG.format(
            time=self.time,
            direction='>',
            name=self.name,
            old=self.old,
            new=self.new,
            class_name=self.class_name,
            length=length,
        )


class CallingMessageRecord(object):
    """ Message record for a change handler call.

    """

    __slots__ = ('time', 'indent', 'handler', 'source')

    def __init__(self, time, indent, handler, source):
        #: Time stamp in UTC.
        self.time = time
        #: Depth level of the call in a chain of trait change dispatches.
        self.indent = indent
        #: The traits change handler that is called.
        self.handler = handler
        #: The source file where the handler was defined.
        self.source = source

    def __unicode__(self):
        gap = self.indent * 2 + SPACES_TO_ALIGN_WITH_CHANGE_MESSAGE
        return CALLINGMSG.format(
            time=self.time,
            action='CALLING',
            handler=self.handler,
            source=self.source,
            gap=gap)


class ExitMessageRecord(object):
    """ Message record for returning from a change event dispatch.

    """

    __slots__ = ('time', 'indent', 'handler', 'exception')

    def __init__(self, time, indent, handler, exception):
        #: Time stamp in UTC.
        self.time = time
        #: Depth level of the exit in a chain of trait change dispatch.
        self.indent = indent
        #: The traits change handler that is called.
        self.handler = handler
        #: The exception type (if one took place)
        self.exception = exception

    def __unicode__(self):
        length = self.indent * 2
        return EXITMSG.format(
            time=self.time,
            direction='<',
            handler=self.handler,
            exception=self.exception,
            length=length,
        )


class RecordContainer(object):
    """ A simple record container.

     This class is commonly used to hold records from a single thread.

    """

    def __init__(self):
        self._records = []

    def record(self, record):
        """ Add the record into the container.

        """

        self._records.append(record)

    def save_to_file(self, filename):
        """ Save the records into a file.

        """
        with open(filename, 'w') as fh:
            for record in self._records:
                fh.write(unicode(record))


class MultiThreadRecordContainer(object):
    """ A container of record containers that are used by separate threads.

    Each record container is mapped to a thread name id. When a RecordContainer
    does not exist for a specific thread a new empty RecordContainer will be
    created on request.


    """

    def __init__(self):
        self._creation_lock = threading.Lock()
        self._record_containers = {}

    def get_change_event_collector(self, thread_name):
        """ Return the dedicated RecordContainer for the thread.

        If no RecordContainer is found for `thread_name` then a new
        RecordContainer is created.

        """
        with self._creation_lock:
            container = self._record_containers.get(thread_name)
            if container is None:
                container = RecordContainer()
                self._record_containers[thread_name] = container
            return container

    def save_to_directory(self, directory_name):
        """ Save records files into the directory.

        Each RecordContainer will dump its records on a separate file named
        <thread_name>.trace.

        """
        with self._creation_lock:
            containers = self._record_containers
            for thread_name, container in containers.iteritems():
                filename = os.path.join(
                    directory_name, '{0}.trace'.format(thread_name))
                container.save_to_file(filename)


class ChangeEventRecorder(object):
    """ A single thread trait change event recorder.

    """

    def __init__(self, container):
        """ Class constructor

        Parameters
        ----------
        container : MultiThreadRecordContainer
           An container to store the records for each trait change.

        """
        self.indent = 1
        self.container = container

    def pre_tracer(self, obj, name, old, new, handler):
        """ Record a string representation of the trait change dispatch

        """
        indent = self.indent
        time = datetime.utcnow().isoformat(' ')
        container = self.container
        container.record(
            ChangeMessageRecord(
                time=time,
                indent=indent,
                name=name,
                old=old,
                new=new,
                class_name=obj.__class__.__name__,
            ),
        )

        container.record(
            CallingMessageRecord(
                time=time,
                indent=indent,
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

        container = self.container

        container.record(
            ExitMessageRecord(
                time=time,
                indent=indent,
                handler=handler.__name__,
                exception=exception_msg,
            ),
        )

        if indent == 1:
            container.record(SentinelRecord())


class MultiThreadChangeEventRecorder(object):
    """ A thread aware trait change recorder.

    The class manages multiple ChangeEventRecorders which record trait change
    events for each thread in a separate file.

    """

    def __init__(self, container):
        """ Object constructor

        Parameters
        ----------
        container : MultiThreadChangeEventRecorder
            The container of RecordContainers to keep the trait change records
            for each thread.

        """
        self.tracers = {}
        self._tracer_lock = threading.Lock()
        self.container = container

    def close(self):
        """ Close and stop all logging.

        """
        with self._tracer_lock:
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
        with self._tracer_lock:
            thread = threading.current_thread().name
            if thread not in self.tracers:
                container = self.container
                thread_container = container.get_change_event_collector(
                    thread)
                tracer = ChangeEventRecorder(thread_container)
                self.tracers[thread] = tracer
                return tracer
            else:
                return self.tracers[thread]


@contextmanager
def record_events():
    """ Multi-threaded trait change event tracer.

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
    container = MultiThreadRecordContainer()
    recorder = MultiThreadChangeEventRecorder(container=container)
    trait_notifiers.set_change_event_tracers(
        pre_tracer=recorder.pre_tracer, post_tracer=recorder.post_tracer)

    try:
        yield container
    finally:
        trait_notifiers.clear_change_event_tracers()
        recorder.close()
