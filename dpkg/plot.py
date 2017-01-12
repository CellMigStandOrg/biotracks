# import needed libraries
import pylab as pl
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

#%matplotlib inline
# sns.set(style="whitegrid")


def prepareforplot(df, x, y, t):
    """Prepare data for visualizations.

    Keyword arguments: (passed through command line for the moment)
    df -- the trajectories dataframe
    x -- the x_coordinate header
    y -- the y_coordinate header
    t -- the time header
    """
    x_coord = x
    y_coord = y
    time = t
    df.sort_values(time, axis=0, inplace=True)


def plotrawtraj(df, joint_id, x_coord, y_coord):
    """Plot the raw trajectories.

    Keyword arguments: (passed through command line for the moment)
    df -- the trajectories dataframe
    joint_id -- the joint_identifier
    """
    grid = sns.FacetGrid(df, hue=joint_id,
                         size=6, palette=sns.color_palette("Set1", 10))
    grid.map(plt.plot, x_coord, y_coord, marker="o", ms=0.3)
    grid.set_xticklabels(rotation=90)
    sns.plt.show()
