#------------------------------------------------------------------------------
# Copyright (c) 2005, Enthought, Inc.
# All rights reserved.
# 
# This software is provided without warranty under the terms of the BSD
# license included in enthought/LICENSE.txt and may be redistributed only
# under the conditions described in the aforementioned license.  The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
# Thanks for using Enthought open source!
# 
# Author: Enthought, Inc.
# Description: <Enthought util package component>
#------------------------------------------------------------------------------
import threading
import time
import unittest 

from enthought.util.Worker import Worker

def slow_eval(worker, sleep_time):
    for i in range(10):
        if worker.abort():
            return
        else:
            # pretend to do some intensive computation 
            time.sleep(sleep_time)
            print worker.getName(),' sleeping for: ', sleep_time
    return sleep_time

snooze = 1

class test_worker_thread(unittest.TestCase):
    
    def check_cancel(self):
        start = time.time()
        worker = Worker(name = "First EnVisage worker thread")
        worker.perform_work(slow_eval, snooze)
        worker.start()   
        time.sleep(3 * snooze)
        worker.cancel()

        worker = Worker(name = "Second EnVisage worker thread")
        worker.perform_work(slow_eval, snooze)
        worker.start()
        time.sleep(2 * snooze)
        worker.cancel()

        duration = time.time() - start
        self.assert_(duration >= 5.0 * snooze)
        self.assert_(duration < 10.0 * snooze)

    def check_concurrent(self):
        start = time.time()
        
        worker = Worker(name = "First EnVisage worker thread")
        worker.perform_work(slow_eval, snooze)
        worker.start()   
    
        worker = Worker(name = "Second EnVisage worker thread")
        worker.perform_work(slow_eval, snooze)
        worker.start()

        duration = time.time() - start
        print duration
        
        # !! todo block on completion and check it is less than twice
        # the time for a single thread

def test_suite(level=1):
    suites = []
    if level > 0:
        suites.append( unittest.makeSuite(test_worker_thread,'check_') )
    if level > 5:
        pass
    total_suite = unittest.TestSuite(suites)
    return total_suite

def test(level=10, verbosity=1):
    all_tests = test_suite(level=level)
    runner = unittest.TextTestRunner(verbosity=verbosity)
    runner.run(all_tests)
    return runner

if __name__ == "__main__":
    test()
