import math
import numpy as np
import matplotlib.pyplot as plt

def curvature(l, alpha):
    return (2*math.sin(alpha))/l


def get_alpha(x, y, yaw, tx, ty):
    pursuit_angle = np.rad2deg(math.atan2(ty - y, tx - x))

    if pursuit_angle < 0 and yaw < 0:
        pursuit_angle *= -1
        pursuit_angle *= -1

    if pursuit_angle < 0:
        pursuit_angle += 360
    if yaw < 0:
        yaw += 360

    alpha = pursuit_angle - yaw

    if alpha > 180:
        alpha -= 360
    if alpha < -180:
        alpha += 360

    return alpha, pursuit_angle


def calc_distance(x0, y0, x1, y1):
    dx = x1 - x0
    dy = y1 - y0
    return math.hypot(dx, dy)


def find_nearest_point(x, y, l, path):

    dx = [tx - x for tx in path.x]
    dy = [ty - y for ty in path.y]

    d = [x**2 + y**2 for x, y in zip(dx, dy)]
    map(math.sqrt, d)

    closest_point_index = d.index(min(d))

    d = 0    
    i = closest_point_index

    while d < l and (i + 1) < len(path.x):

        d = calc_distance(x, y, path.x[i], path.y[i])

        if d < l:
            i += 1

    tx = path.x[i]
    ty = path.y[i]

    return [tx, ty]


def get_control_signal(x, y, l, yaw, path):
   tx, ty = find_nearest_point(x, y, l, path)
   return get_alpha(x, y, tx, ty, yaw), tx, ty


