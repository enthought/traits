from threading import Thread
from time import sleep
from traits.api import *
from traitsui.api import View, Item, ButtonEditor

class TextDisplay(HasTraits):
    string = String()

    view= View( Item('string',show_label=False, springy=True, style='custom' ))

class CaptureThread(Thread):
    def run(self):
        self.display.string = 'Camera started\n' + self.display.string  n_img = 0
        while not self.wants_abort:
            sleep(.5)
            n_img += 1
            self.display.string = '%d image captured\n' % n_img \ + self.display.string
        self.display.string = 'Camera stopped\n' + self.display.string

class Camera(HasTraits):
    start_stop_capture = Button()
    display = Instance(TextDisplay)
    capture_thread = Instance(CaptureThread)

    view = View( Item('start_stop_capture', show_label=False ))

    def _start_stop_capture_fired(self):
    if self.capture_thread and self.capture_thread.isAlive():
        self.capture_thread.wants_abort = True
    else:
        self.capture_thread = CaptureThread()
        self.capture_thread.wants_abort = False
        self.capture_thread.display = self.display
        self.capture_thread.start()

class MainWindow(HasTraits):
    display = Instance(TextDisplay, ())

    camera = Instance(Camera)

    def _camera_default(self):
        return Camera(display=self.display)

    view = View('display', 'camera', style="custom", resizable=True)

    if __name__ == '__main__':
        MainWindow().configure_traits()
