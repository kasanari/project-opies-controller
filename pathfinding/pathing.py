import numpy as np
import matplotlib.pyplot as plt
import time

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
        total_path_x = np.concatenate(total_path_x, path_x, axis=1)
        total_path_y = np.concatenate(total_path_y, path_y, axis=1)

    plt.plot(x_points, y_points, 'o')
    plt.plot(total_path_x, total_path_y)
    plt.show()


np.random.seed(int(time.time()))

path_x = np.linspace(0, 2*np.pi, 10)
path_y = np.sin(path_x)


create_path_from_points(path_x, path_y)