from traits.api import *
from traitsui.api import *

class Camera(HasTraits):
    """ Camera object """

    gain = Enum(1, 2, 3,
        desc="the gain index of the camera",
        label="gain", )

    exposure = CInt(10,
        desc="the exposure time, in ms",
        label="Exposure", )

class Display(HasTraits):
    string = String()

    view= View( Item('string', show_label=False, springy=True, style='custom' ))

class Container(HasTraits):
    camera = Instance(Camera, ())
    display = Instance(Display, ())

    view = View(
                Item('camera', style='custom', show_label=False, ),
                Item('display', style='custom', show_label=False, ),
               )

Container().configure_traits()

