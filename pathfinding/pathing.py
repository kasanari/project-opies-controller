import numpy as np
import matplotlib.pyplot as plt
import time
from dataclasses import dataclass

from matplotlib.animation import MovieWriter, FFMpegWriter

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

        total_path_x = np.concatenate((total_path_x, path_x), axis=None)
        total_path_y = np.concatenate((total_path_y, path_y), axis=None)


    path = Path(total_path_x, total_path_y)
    return path

def plot_path(ax, x_points, y_points, path):
    ax.plot(x_points, y_points, 'ro')
    ax.plot(path.x, path.y, 'bx')

def create_circle(x, y, l):
    circle1 = plt.Circle((x, y), l, color='r', fill=False)
    plt.gcf().gca().add_artist(circle1)
    return circle1

def update_graph(x, y, tx, ty, target_line, car, circle, alpha):
    plt.title(f'alpha: {alpha}')
    target_line.set_data([x,tx], [y,ty])
    car.set_data(x, y)
    circle.center = (x,y)

def test_pure_pursuit():

    np.random.seed(int(time.time()))

    points_x = [0, 1.5, 3]
    points_y = [1.5, 2, 1.5]

    fig, ax = plt.subplots(1,1)
    ax.set_aspect('equal')
    plt.xlim([0, 3])
    plt.ylim([0, 3])

    path = create_path_from_points(points_x, points_y)

    x, y = 0.5, 1.25
    yaw = np.deg2rad(0)
    l = 0.75

    tx, ty = pp.find_nearest_point(x, y, l, path)

    alpha = pp.get_alpha(x, y, yaw, tx, ty)
    print(np.rad2deg(alpha))

    moviewriter = FFMpegWriter(fps=30)
    moviewriter.setup(fig, 'my_movie.mp4', dpi=100)

    plot_path(ax, points_x, points_y, path)
    target_line, = ax.plot([x, tx], [y, ty], 'g')
    car, = ax.plot(x, y, 'o')
    circle = create_circle(x,y,l)

    while x < 3:

        tx, ty = pp.find_nearest_point(x, y, l, path)

        alpha = pp.get_alpha(x, y, yaw, tx, ty)

        update_graph(x, y, tx, ty, target_line, car, circle, alpha)

        moviewriter.grab_frame()
        x += 0.05 * np.cos(alpha)
        y += 0.05 * np.sin(alpha)


    moviewriter.finish()

    plt.show()

test_pure_pursuit()
