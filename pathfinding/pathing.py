import numpy as np

def create_path():
   spacing = 10
   x_vals = np.linspace(-1, 1, num=spacing)
   y_vals = [1-x*x for x in x_vals]
   gradients = np.gradient(y_vals, spacing)
   path = zip(x_vals, y_vals, gradients)
   return list(path)
