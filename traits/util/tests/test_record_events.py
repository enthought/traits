# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

import os
import shutil
import tempfile
import threading
import unittest

from traits.api import HasTraits, on_trait_change, Bool, Float, List
from traits import trait_notifiers
from traits.util.event_tracer import (
    ChangeEventRecorder,
    MultiThreadChangeEventRecorder,
    MultiThreadRecordContainer,
    RecordContainer,
    record_events,
)


class TestObject(HasTraits):

    number = Float(2.0)
    list_of_numbers = List(Float())
    flag = Bool

    @on_trait_change("number")
    def _add_number_to_list(self, value):
        self.list_of_numbers.append(value)

    def add_to_number(self, value):
        self.number += value


class TestRecordEvents(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.directory)

    def test_change_event_recorder(self):
        test_object = TestObject()
        container = RecordContainer()
        recorder = ChangeEventRecorder(container=container)
        trait_notifiers.set_change_event_tracers(
            pre_tracer=recorder.pre_tracer, post_tracer=recorder.post_tracer
        )
        try:
            test_object.number = 5.0
        finally:
            trait_notifiers.clear_change_event_tracers()

        filename = os.path.join(self.directory, "MainThread.trace")
        container.save_to_file(filename)
        with open(filename, "r", encoding="utf-8") as handle:
            lines = handle.readlines()
            self.assertEqual(len(lines), 4)
            # very basic checking
            self.assertTrue(
                "-> 'number' changed from 2.0 to 5.0 in 'TestObject'\n"
                in lines[0]
            )
            self.assertTrue("CALLING" in lines[1])
            self.assertTrue("EXIT" in lines[2])

    def test_multi_thread_change_event_recorder(self):
        test_object = TestObject()
        container = MultiThreadRecordContainer()
        recorder = MultiThreadChangeEventRecorder(container=container)
        trait_notifiers.set_change_event_tracers(
            pre_tracer=recorder.pre_tracer, post_tracer=recorder.post_tracer
        )
        try:
            test_object.number = 5.0
            thread = threading.Thread(
                target=test_object.add_to_number, args=(5,)
            )
            thread.start()
            thread.join()
        finally:
            trait_notifiers.clear_change_event_tracers()
        self.assertEqual(len(container._record_containers), 2)

        # save records
        container.save_to_directory(self.directory)
        for name in container._record_containers:
            filename = os.path.join(self.directory, "{0}.trace".format(name))
            with open(filename, "r", encoding="utf-8") as handle:
                lines = handle.readlines()
            self.assertEqual(len(lines), 4)
            # very basic checking
            if "MainThread.trace" in filename:
                self.assertTrue(
                    "-> 'number' changed from 2.0 to 5.0 in 'TestObject'\n"
                    in lines[0]
                )
            else:
                self.assertTrue(
                    "-> 'number' changed from 5.0 to 10.0 in 'TestObject'\n"
                    in lines[0]
                )
            self.assertTrue("CALLING" in lines[1])
            self.assertTrue("EXIT" in lines[2])

    def test_record_events(self):
        test_object = TestObject()
        with record_events() as container:
            test_object.number = 5.0
            thread = threading.Thread(
                target=test_object.add_to_number, args=(3,)
            )
            thread.start()
            thread.join()

        # save records
        container.save_to_directory(self.directory)
        for name in container._record_containers:
            filename = os.path.join(self.directory, "{0}.trace".format(name))
            with open(filename, "r", encoding="utf-8") as handle:
                lines = handle.readlines()
            self.assertEqual(len(lines), 4)
            # very basic checking
            if "MainThread.trace" in filename:
                self.assertTrue(
                    "-> 'number' changed from 2.0 to 5.0 in 'TestObject'\n"
                    in lines[0]
                )
            else:
                self.assertTrue(
                    "-> 'number' changed from 5.0 to 8.0 in 'TestObject'\n"
                    in lines[0]
                )
            self.assertTrue("CALLING" in lines[1])
            self.assertTrue("EXIT" in lines[2])
