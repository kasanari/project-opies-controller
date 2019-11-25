import numpy as np
import matplotlib.pyplot as plt

def create_path():
   spacing = 10
   x_vals = np.linspace(0, 2, num=spacing)
   y_vals = [2-(x-1)*(x-1) for x in x_vals]
   gradients = np.gradient(y_vals, spacing)
   plt.plot(x_vals, y_vals)
   plt.show()


   path = zip(x_vals, y_vals, np.rad2deg(np.arctan(gradients)))
   return list(path)


path = create_path()
print(path)