# import needed libraries
import pylab as pl
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import pandas as pd

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


def plotXY(df, joint_id, x_coord, y_coord):
    """Plot the raw trajectories.

    df -- the trajectories dataframe
    joint_id -- the joint_identifier
    x_coord -- the x coordinate
    y_coord -- the y coordinate
    """
    grid = sns.FacetGrid(df, hue=joint_id,
                         size=6, palette=sns.color_palette("Set1", 10))
    grid.fig.suptitle('XY trajectories')
    grid.map(plt.plot, x_coord, y_coord, marker="o", ms=0.3)
    grid.set_xticklabels(rotation=90)
    sns.plt.show()


def normalize(df, joint_id, x_coord, y_coord):
    """Normalize to the origin.

    df -- the trajectories dataframe
    joint_id -- the joint_identifier
    x_coord -- the x coordinate
    y_coord -- the y coordinate
    """
    list_ = []
    x_norm = x_coord + 'norm'
    y_norm = y_coord + 'norm'
    for track in df[joint_id].unique():
        temp_tracks = df[df[joint_id] == track]
        # the first x and y values
        x0, y0 = temp_tracks.iloc[0][x_coord], temp_tracks.iloc[0][y_coord]
        for index, row in temp_tracks.iterrows():
            current_x, current_y = row[x_coord], row[y_coord]
            xn, yn = current_x - x0, current_y - y0

            # pass a list to .loc to be sure to get a dataframe: behavior is
            # not consistent!
            temp_tracks_row = temp_tracks.loc[[index]]
            temp_tracks_row[x_norm], temp_tracks_row[y_norm] = xn, yn
            list_.append(temp_tracks_row)

    df = pd.concat(list_)
    return df
