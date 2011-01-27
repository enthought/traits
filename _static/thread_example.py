from threading import Thread
from time import sleep

class MyThread(Thread):
    def run(self):
        sleep(2)
        print "MyThread done"

my_thread = MyThread()

my_thread.start()
print "Main thread done"

