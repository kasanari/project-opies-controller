import pandas as pd
import matplotlib.pyplot as plt

data: pd.DataFrame = pd.read_csv("Thu_Nov_28_120204_2019.csv")

x = data['x']

variance_x = data['x'].var()
variance_y = data['y'].var()

print(variance_x)
print(variance_y)

colors = data['quality']

data.plot(x='x', y='y', kind='scatter', c=colors, colormap='plasma')
plt.ylim(0, 2)
plt.xlim(0, 2)
plt.savefig(f"scatter_test.png")

fig, ax = plt.subplots(1, 1)

data.reset_index().plot.scatter(ax=ax, x='index', y=['x'], marker='o', c=colors, colormap='plasma')
data.reset_index().plot.scatter(ax=ax, x='index', y=['y'], marker='o', c=colors, colormap='plasma')
data.reset_index().plot.line(ax=ax, x='index', y=['x_kf', 'y_kf', 'target'])
plt.savefig(f"line_plot_test.png")
fig.set_size_inches(15, 7, forward=True)
# data.reset_index().plot.scatter(ax=ax, x='index', y=['x_kf', 'y_kf', 'target'])


# data.reset_index().plot(ax=ax, x='index', y=['quality'])
