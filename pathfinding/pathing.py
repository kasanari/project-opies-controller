import math
from dataclasses import dataclass

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FFMpegWriter

import pathfinding.pure_pursuit as pp


@dataclass
class Path:
    x: np.ndarray
    y: np.ndarray

    def __init__(self, x_points, y_points):
        if not isinstance(x_points, list) or len(x_points) == 1:
            self.x = x_points
            self.y = y_points
            return
        if len(x_points) != len(y_points):
            raise RuntimeError("Number of x points are not equal to the number of y points!")
        else:
            total_path_x = []
            total_path_y = []

            x_points = [int(x * 100) for x in x_points]
            y_points = [int(y * 100) for y in y_points]

            for n in range(0, len(x_points)-1): #not an off by one error

                for x, y in bresenham(x_points[n], y_points[n], x_points[n + 1], y_points[n + 1]):
                    total_path_x.append(x / 100)
                    total_path_y.append(y / 100)

            self.x = total_path_x
            self.y = total_path_y

    def __len__(self):
        return len(self.x)

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


def plot_path(ax, x_points, y_points, path):
    ax.plot(x_points, y_points, 'ro')
    ax.plot(path.x, path.y, 'bx')


def create_circle(x, y, l):
    circle1 = plt.Circle((x, y), l, color='r', fill=False)
    plt.gcf().gca().add_artist(circle1)
    return circle1


def update_graph(x, y, yaw, tx, ty, target_line, heading_line, car, circle, alpha, l):
    target_line.set_data([x,tx], [y,ty])
    heading_line.set_data([x, x+0.5*math.cos(np.deg2rad(yaw))], [y, y+0.5*math.sin(np.deg2rad(yaw))])
    car.set_data(x, y)
    circle.center = (x,y)


def plot_pure_pursuit(x_vals, y_vals, yaw_vals, points_x, points_y, lookahead, filename="my_movie", ):
    fig, ax = plt.subplots(1, 1)
    ax.set_aspect('equal')
    plt.xlim([0, 6])
    plt.ylim([0, 6])

    path = Path(points_x, points_y)

    x_0 = x_vals[0]
    y_0 = y_vals[0]
    yaw_0 = yaw_vals[0]

    l = lookahead

    tx, ty = pp.find_nearest_point(x_0, y_0, l, path)

    moviewriter = FFMpegWriter(fps=30)
    moviewriter.setup(fig, f'{filename}.mp4', dpi=100)

    plot_path(ax, points_x, points_y, path)
    target_line, = ax.plot([x_0, tx], [y_0, ty], 'g')
    heading_line, = ax.plot([x_0, x_0+0.5*math.cos(np.deg2rad(yaw_0))], [y_0, y_0+0.5*math.sin(np.deg2rad(yaw_0))])
    car, = ax.plot(x_0, y_0, 'o')
    circle = create_circle(x_0, y_0, l)

    for x, y, yaw in zip(x_vals, y_vals, yaw_vals):

        tx, ty = pp.find_nearest_point(x, y, l, path)

        alpha = pp.get_alpha(x, y, yaw, tx, ty)
        ax.set_title(f'alpha, heading: {alpha} \n x,y,yaw: {(x, y, yaw)}')
        update_graph(x, y, yaw, tx, ty, target_line, heading_line, car, circle, alpha, l)

        moviewriter.grab_frame()

    moviewriter.finish()


