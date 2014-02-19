#------------------------------------------------------------------------------
# Copyright (c) 2005-2013, Enthought, Inc.
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in /LICENSE.txt and may be redistributed only
# under the conditions described in the aforementioned license.  The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
# Thanks for using Enthought open source!
#------------------------------------------------------------------------------
import os
import shutil
import tempfile
import unittest

from traits.api import HasTraits, on_trait_change, Bool, Float, List
from traits.util.event_tracer import record_events


class TestObject(HasTraits):

    number = Float(2.0)
    list_of_numbers = List(Float())
    flag = Bool

    @on_trait_change('number')
    def _add_number_to_list(self, value):
        self.list_of_numbers.append(value)

    def add_to_number(self, value):
        self.number += value


class TestRecordEvents(unittest.TestCase):

    def setUp(self):
        self.directory = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.directory)

    def test_record_events_on_single_thread(self):
        test_object = TestObject()
        with record_events() as container:
            test_object.number = 5.0
        container.save_to_directory(self.directory)
        trace_files = os.listdir(self.directory)
        self.assertEqual(trace_files, ['MainThread.trace'])
        main_trace = os.path.join(self.directory, trace_files[0])
        with open(main_trace, 'Ur') as handle:
            lines = handle.readlines()
            # very basic checking
            self.assertEqual(len(lines), 4)
            self.assertIn(' ->', lines[0])
            self.assertIn('CALLING', lines[1])
            self.assertIn('EXIT', lines[2])


if __name__ == '__main__':
    unittest.main()
