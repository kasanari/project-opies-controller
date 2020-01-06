from analysis.data_logger import DataLogger
import pandas as pd

from pathfinding.pathing import plot_pure_pursuit
import os

def test_plot_path():
    data_logger = DataLogger()
    lookahead = 0.8
    path = {
        "x": [1.6, 2.9, 2.9, 1.6, 1.6],
        "y": [1.5, 1.5, 5.0, 5.0, 1.5]
    }
    if os.path.isfile("test.mp4"):
        os.remove("test.mp4")
    data_logger.df = pd.read_csv(r"C:\Users\Jakob\Documents\GitHub\project-opies-controller\analysis\data\Thu_Jan__2_095217_2020.csv")
    #data_logger.plot_path(path, filename="test")
    plot_pure_pursuit(data_logger.df.reset_index()["x"],
                      data_logger.df.reset_index()["y"],
                      data_logger.df.reset_index()["yaw"],
                      path["x"], path["y"], lookahead=lookahead, filename="test")
