import math

lookahead = 0.2

def curvature(l, alpha):
    return (2*math.sin(alpha))/l

def get_control_signal(x, y, yaw, target):

    alpha = math.atan2(target.y - y, target.x - x) - yaw


def find_nearest_point(x,y, path):

    d_x = []
    d_y =

