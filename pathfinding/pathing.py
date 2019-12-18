import numpy as np
import matplotlib.pyplot as plt
import time
from dataclasses import dataclass
import pathfinding.pure_pursuit as pp
import math

@dataclass
class Path:
    x: np.ndarray
    y: np.ndarray

def bresenham(x0, y0, x1, y1):
    """Yield integer coordinates on the line from (x0, y0) to (x1, y1).
    Input coordinates should be integers.
    The result will contain both the start and the end point.
    """
    dx = x1 - x0
    dy = y1 - y0

    xsign = 1 if dx > 0 else -1
    ysign = 1 if dy > 0 else -1

    dx = abs(dx)
    dy = abs(dy)

    if dx > dy:
        xx, xy, yx, yy = xsign, 0, 0, ysign
    else:
        dx, dy = dy, dx
        xx, xy, yx, yy = 0, ysign, xsign, 0

    D = 2*dy - dx
    y = 0

    for x in range(dx + 1):
        yield x0 + x*xx + y*yx, y0 + x*xy + y*yy
        if D >= 0:
            y += 1
            D -= 2*dx
        D += 2*dy


def line(x0, y0, x1, y1):

    vals = np.linspace(x0, x1, 10)
    path = np.interp(vals, [x0, x1], [y0, y1])
    return [vals, path]


def plot_line(x0, y0, x1, y1):
    dx = x1 - x0
    dy = y1 - y0

    dx = abs(dx)
    dy = abs(dy)

    if dy < dx:
        if x0 > x1:
            return line(x1, y1, x0, y0)
        else:
            return line(x0, y0, x1, y1)
    else:
        if y0 > y1:
            return line(x1, y1, x0, y0)
        else:
            return line(x0, y0, x1, y1)


def create_path():
    spacing = 10
    x_vals = np.linspace(-1, 1, num=spacing)
    y_vals = [1 - x * x for x in x_vals]
    gradients = np.gradient(y_vals, spacing)
    path = zip(x_vals, y_vals, gradients)
    return list(path)


def create_path_from_points(x_points, y_points):

    total_path_x = np.array([])
    total_path_y = np.array([])

    for n in range(0, len(x_points)-1):

        path_x, path_y = plot_line(x_points[n], y_points[n], x_points[n+1], y_points[n+1])
        plt.plot(path_x, path_y, 'x')

        total_path_x = np.concatenate((total_path_x, path_x), axis=None)
        total_path_y = np.concatenate((total_path_y, path_y), axis=None)

    plt.plot(x_points, y_points, 'o')

    path = Path(total_path_x, total_path_y)

    x, y = 0.5, 1.25
    yaw = np.deg2rad(0)
    l = 0.5

    tx, ty = pp.find_nearest_point(x, y, l, path)
    alpha = pp.get_alpha(x, y, yaw, tx, ty)
    print(alpha)
    circle1 = plt.Circle((x, y), l, color='r', fill=False)
    plt.gcf().gca().add_artist(circle1)



    plt.plot(x,y,'o')
    plt.plot([x, tx], [y, ty])
    plt.show()

    return path


np.random.seed(int(time.time()))

#path_x = np.linspace(0, 2*np.pi, 10)
#path_y = np.sin(path_x)

path_x = [0, 1, 2]
path_y = [1.5, 2, 1.5]

plt.xlim([0, 3])
plt.ylim([0, 3])


create_path_from_points(path_x, path_y)