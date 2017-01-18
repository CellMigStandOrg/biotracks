# import needed libraries
import pylab as pl
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import pandas as pd
import math


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
    grid.map(plt.plot, x_coord, y_coord, marker=".", ms=0.3)
    grid.map(plt.scatter, x_coord, y_coord, marker="o", s=20)
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


def compute_ta(df, joint_id, x_coord, y_coord):
    """Compute turning angles.

    df -- the trajectories dataframe
    joint_id -- the joint_identifier
    x_coord -- the x coordinate
    y_coord -- the y coordinate
    """
    list_ = []
    for track in df[joint_id].unique():
        temp = pd.DataFrame()
        temp_tracks = df[df[joint_id] == track]
        for i, row in enumerate(temp_tracks.iterrows()):
            temp_tracks_row = temp_tracks.iloc[[i]]
            if i == 0:
                previousX, previousY = row[1][x_coord], row[1][y_coord]
                temp.loc[i, 'ta'] = float('NaN')
            else:
                delta_x, delta_y = row[1][x_coord] - \
                    previousX, row[1][y_coord] - previousY
                previousX, previousY = row[1][x_coord], row[1][y_coord]
                ta = math.atan2(delta_y, delta_x)
                temp.loc[i, 'ta'] = ta

            list_.append(temp)

    df = pd.concat(list_)
    return df


def plot_polar(theta, N):
    """Plot polar plot.

    theta -- the dataframe with the turning angles
    N -- number of bins to use
    """
    hist, bins = np.histogram(theta.ta, bins=N)

    # the width of the bins interval
    width = [t - s for s, t in zip(bins, bins[1:])]
    bins_ = bins[0:N]  # exclude the last value

    # the actual plotting logic
    g = sns.FacetGrid(theta, size=4)

    radii = hist / max(hist)

    for ax in g.axes.flat:
        ax2 = plt.subplot(111, projection='polar')
        bars = ax2.bar(bins_, radii, width, bottom=0.0)
        for r, bar in zip(radii, bars):
            bar.set_facecolor(plt.cm.Spectral(r))
            bar.set_alpha(0.5)

    sns.plt.show()
