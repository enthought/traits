# (C) Copyright 2005-2020 Enthought, Inc., Austin, TX
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

from traits.util.event_tracer import (
    SentinelRecord,
    RecordContainer,
    MultiThreadRecordContainer,
)


class TestRecordContainers(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.mkdtemp()
        self.filename = os.path.join(self.directory, "myfile")

    def tearDown(self):
        shutil.rmtree(self.directory)

    def test_record_container(self):
        container = RecordContainer()

        # add records
        for i in range(7):
            container.record(SentinelRecord())
        self.assertEqual(len(container._records), 7)

        # save records
        container.save_to_file(self.filename)

        with open(self.filename, "r", encoding="utf-8") as handle:
            lines = handle.readlines()
        self.assertEqual(lines, ["\n"] * 7)

    def test_multi_thread_record_container(self):
        container = MultiThreadRecordContainer()

        def record(container):
            thread = threading.current_thread().name
            collector = container.get_change_event_collector(thread)
            collector.record(SentinelRecord())

        thread_1 = threading.Thread(target=record, args=(container,))
        thread_2 = threading.Thread(target=record, args=(container,))
        thread_1.start()
        thread_2.start()
        record(container)
        thread_2.join()
        thread_1.join()

        self.assertEqual(len(container._record_containers), 3)
        for collector in container._record_containers.values():
            self.assertTrue(isinstance(collector._records[0], SentinelRecord))
            self.assertEqual(len(collector._records), 1)

        # save records
        container.save_to_directory(self.directory)
        for name in container._record_containers:
            filename = os.path.join(self.directory, "{0}.trace".format(name))
            with open(filename, "r", encoding="utf-8") as handle:
                lines = handle.readlines()
            self.assertEqual(lines, ["\n"])
