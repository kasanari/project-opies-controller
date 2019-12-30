from analysis.data_logger import DataLogger
import pandas as pd

from pathfinding.pathing import plot_pure_pursuit


def test_plot_path():
    data_logger = DataLogger()
    path = {
        "x": [3, 3, 3],
        "y": [2, 3, 4]
    }
    data_logger.df = pd.read_csv(r"C:\Users\Jakob\Documents\GitHub\project-opies-controller\analysis\Mon_Dec_30_111820_2019.csv")
    data_logger.plot_path(path, filename="test")
    plot_pure_pursuit(data_logger.df.reset_index()["x"],
                      data_logger.df.reset_index()["y"],
                      data_logger.df.reset_index()["yaw"],
                      path["x"], path["y"])
