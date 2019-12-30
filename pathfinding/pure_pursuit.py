import math
import matplotlib.pyplot as plt

def curvature(l, alpha):
    return (2*math.sin(alpha))/l


def get_alpha(x, y, yaw, tx, ty):
    alpha = math.atan2(ty - y, tx - x) - yaw
    return alpha


def find_nearest_point(x,y, l, path):

    dx = [tx - x for tx in path.x]
    dy = [ty - y for ty in path.y]

    d = [x**2 + y**2 for x, y in zip(dx, dy)]
    map(math.sqrt, d)

    closed_point_index = d.index(min(d))

    d = 0
    i = closed_point_index

    while d < l and (i + 1) < len(path.x):

        dx = x - path.x[i]
        dy = y - path.y[i]
        d = math.hypot(dx, dy)

        if d < l:
            i += 1

    tx = path.x[i]
    ty = path.y[i]

    return [tx, ty]


def get_control_signal(x, y, l, yaw, path):
   tx, ty = find_nearest_point(x, y, l, path)
   return get_alpha(x, y, tx, ty, yaw), tx, ty


