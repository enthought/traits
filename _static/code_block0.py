from numpy import cos, sin

class Point(object):
    """ 3D Points objects """
    x = 0.
    y = 0.
    z = 0.

    def rotate_z(self, theta):
        """ rotate the point around the Z axis """
        xtemp =  cos(theta) * self.x + sin(theta) * self.y
        ytemp = -sin(theta) * self.x + cos(theta) * self.y
        self.x = xtemp
        self.y = ytemp

