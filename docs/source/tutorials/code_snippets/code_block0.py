from numpy import cos, sin

class Point(object):
    """ 3D Points objects """
    x = 0.
    y = 0.
    z = 0.

    def rotate_z(self, theta):
        """ rotate the point around the Z axis """
        self.x =  cos(theta) * self.x + sin(theta) * self.y
        self.y = -sin(theta) * self.x + cos(theta) * self.y
        
