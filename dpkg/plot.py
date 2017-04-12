# import needed libraries
import math

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pylab as pl
import seaborn as sns


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


def plotXY(df, id_, x_coord, y_coord):
    """Plot the raw trajectories.

    df -- the trajectories dataframe
    id_ -- an identifier (for linear connections of objects)
    x_coord -- the x coordinate
    y_coord -- the y coordinate
    """
    grid = sns.FacetGrid(df, hue=id_,
                         size=6, palette=sns.color_palette("Set1", 10))
    grid.fig.suptitle('XY trajectories')
    grid.map(plt.plot, x_coord, y_coord, marker=".", ms=0.3)
    grid.map(plt.scatter, x_coord, y_coord, marker="o", s=20)
    grid.set_xticklabels(rotation=90)
    sns.plt.show()


def normalize(df, id_, x_coord, y_coord):
    """Normalize to the origin.

    df -- the trajectories dataframe
    id_ -- an identifier (linkID or trackID)
    x_coord -- the x coordinate
    y_coord -- the y coordinate
    """
    list_ = []
    x_norm = x_coord + 'norm'
    y_norm = y_coord + 'norm'
    df = df.dropna()
    for i in df[id_].unique():
        tmp = df[df[id_] == i]
        # the first x and y values
        x0, y0 = tmp.iloc[0][x_coord], tmp.iloc[0][y_coord]
        for index, row in tmp.iterrows():
            current_x, current_y = row[x_coord], row[y_coord]
            xn, yn = current_x - x0, current_y - y0
            # pass a list to .loc to be sure to get a dataframe: behavior is
            # not consistent!
            tmp_row = tmp.loc[[index]]
            tmp_row[x_norm], tmp_row[y_norm] = xn, yn
            list_.append(tmp_row)

    df = pd.concat(list_)
    return df

def cum_displ(df, id_, x_coord, y_coord):
    list_ = []
    x_cum = x_coord + 'cum'
    y_cum = y_coord + 'cum'
    for i in df[id_].unique():
        tmp = df[df[id_] == i]
        cumX = 0
        cumY = 0
        for index, row in tmp.iterrows():
            current_x, current_y = row[x_coord], row[y_coord]
            tmp_row = tmp.loc[[index]]

            cumX+=current_x
            cumY+=current_y
            tmp_row[x_cum], tmp_row[y_cum] = cumX, cumY
            list_.append(tmp_row)

    df = pd.concat(list_)
    return df

def compute_ta(df, id_, x_coord, y_coord):
    """Compute turning angles.

    df -- the trajectories dataframe
    id_ -- an identifier
    x_coord -- the x coordinate
    y_coord -- the y coordinate
    """
    list_ = []
    for i in df[id_].unique():
        tmp_df = pd.DataFrame()
        tmp = df[df[id_] == i]
        for i, row in enumerate(tmp.iterrows()):
            temp_tracks_row = tmp.iloc[[i]]
            if i == 0:
                previousX, previousY = row[1][x_coord], row[1][y_coord]
                tmp_df.loc[i, 'ta'] = float('NaN')
            else:
                delta_x, delta_y = row[1][x_coord] - \
                    previousX, row[1][y_coord] - previousY
                previousX, previousY = row[1][x_coord], row[1][y_coord]
                ta = math.atan2(delta_y, delta_x)
                tmp_df.loc[i, 'ta'] = ta

            list_.append(tmp_df)

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
