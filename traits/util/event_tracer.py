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
from contextlib import contextmanager
import inspect
import os
import threading
from datetime import datetime

from traits import trait_notifiers

CHANGEMSG = (
    u"{time} {direction:-{direction}{length}} '{name}' changed from "
    u"{old} to {new} in '{class_name}'{sep}")
CALLINGMSG = u"{time} {action:>{gap}}: '{handler}' in {source}{sep}"
EXITMSG = (
    u"{time} {direction:-{direction}{length}} "
    u"EXIT: '{handler}'{exception}{sep}")


class ChangeEventRecorder(object):
    """ A thread aware trait change recorder

    The class manages multiple ThreadChangeEventRecorders which record
    trait change events for each thread in a separate file.

    """

    def __init__(self, trace_directory):
        """ Object constructor

        Parameters
        ----------
        trace_directory : string
            The directory where the change log for each thread will be saved

        """
        self.tracers = {}
        self.tracer_lock = threading.Lock()
        self.trace_directory = trace_directory

    def close(self):
        """ Close log files.

        """
        with self.tracer_lock:
            tracers = self.tracers
            self.tracers = {}
            for tracer in tracers.values():
                tracer.fh.close()

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
                filename = os.path.join(self.trace_directory,
                                        '{}.trace'.format(thread))
                fh = open(filename, 'wb')
                tracer = ThreadChangeEventRecorder(fh)
                self.tracers[thread] = tracer
                return tracer
            else:
                return self.tracers[thread]


class ThreadChangeEventRecorder(object):
    """ A single thread trait change event recorder.

    """


    def __init__(self, fh):
        """ Class constructor

        Parameters
        ----------
        fh : stream
           An io stream to store the records for each trait change.

        """
        self.indent = 1
        self.fh = fh

    def pre_tracer(self, obj, name, old, new, handler):
        """ Record a string representation of the trait change dispatch

        """
        indent = self.indent
        time = datetime.utcnow().isoformat(' ')
        handle = self.fh
        handle.write(
            CHANGEMSG.format(
                time=time,
                direction='>',
                length=indent*2,
                name=name,
                old=old,
                new=new,
                class_name=obj.__class__.__name__,
                sep=os.linesep,
            ).encode('utf-8'),
        )
        handle.write(
            CALLINGMSG.format(
                time=time,
                gap=indent*2 + 9,
                action='CALLING',
                handler=handler.__name__,
                source=inspect.getsourcefile(handler),
                sep=os.linesep,
            ).encode('utf-8'),
        )
        self.indent += 1

    def post_tracer(self, obj, name, old, new, handler, exception=None):
        """ Record a string representation of the trait change return

        """
        time = datetime.utcnow().isoformat(' ')
        self.indent -= 1
        handle = self.fh
        indent = self.indent
        if exception:
            exception_msg = ' [EXCEPTION: {}]'.format(exception)
        else:
            exception_msg = ''

        handle.write(
            EXITMSG.format(
                time=time,
                direction='<',
                length=indent*2,
                handler=handler.__name__,
                exception=exception_msg,
                sep=os.linesep,
            ).encode('utf-8'),
        )
        if indent == 1:
            handle.write(u'{0}'.format(os.linesep).encode('utf-8'))


@contextmanager
def record_events(trace_directory):
    """ Multi-threaded trait event tracer

    Parameters
    ----------
    trace_directory : string
        The directory where the change log for each event will be saved


    Usage
    -----
    ::

        >>> from trace_recorder import record_events
        >>> with record_events('C:\\dev\\trace'):
        ...     my_model.some_trait = True

    This will install a tracer that will record all events that occur from
    setting of some_trait on the my_model instance.

    The results will be stored in one file per running thread in the
    directory 'C:\\dev\\trace'.  The files are named after the thread being
    traced.

    """
    recorder = ChangeEventRecorder(trace_directory)
    trait_notifiers.set_change_event_tracers(
        pre_tracer=recorder.pre_tracer, post_tracer=recorder.post_tracer)

    try:
        yield
    finally:
        trait_notifiers.clear_change_event_tracers()
        recorder.close()
