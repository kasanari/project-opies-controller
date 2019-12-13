import matplotlib.pyplot as plt
import pandas as pd

data: pd.DataFrame = pd.read_csv("Thu_Nov_28_155509_2019.csv", index_col=0)

data.plot(y='y')

plt.show()
data.index = pd.to_datetime(data.index)

diffs = data.reset_index().diff(periods=3)

diffs['index'] = pd.to_timedelta(diffs['index'], unit='s')

velocities = diffs['y']/diffs['index'].dt.microseconds

velocities *= 10E6

print(max(velocities))

plt.plot(velocities)
plt.show()
