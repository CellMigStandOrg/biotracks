# #%L
# Copyright (c) 2016-2017 Cell Migration Standardisation Organization
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
# #L%

import math

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


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
    sns.plt.savefig("trajectories.png")


def normalize(df, id_, x_coord, y_coord):
    """Normalize to the origin of the coordinate system.

    df -- the trajectories dataframe
    id_ -- an identifier (linkID or trackID)
    x_coord -- the x coordinate
    y_coord -- the y coordinate
    """
    list_ = []
    df = df.dropna()
    for i in df[id_].unique():
        tmp = df[df[id_] == i]
        # convert coordinates columns into numpy array
        array = tmp[[x_coord, y_coord]].values
        # substract first x and y coordinates
        diff_array = array - array[0]
        diff_df = pd.DataFrame(diff_array, columns=['x_norm', 'y_norm'])
        tmp = tmp.assign(x_norm=diff_df.x_norm.values,
                         y_norm=diff_df.y_norm.values)
        list_.append(tmp)
    result = pd.concat(list_)
    return result


def compute_cumulative_displacements(df, id_, x_coord, y_coord):
    """Compute cumulative displacements of motion in the two directions, x
    and y.

    df -- the trajectories dataframe
    id_ -- an identifier
    x_coord -- the x coordinate
    y_coord -- the y coordinate
    """
    list_ = []

    df = df.dropna()
    for i in df[id_].unique():
        tmp = df[df[id_] == i]
        # convert coordinates columns into numpy array
        array = tmp[[x_coord, y_coord]].values
        # add rows
        sum_array = np.cumsum(array, axis=0)
        sum_df = pd.DataFrame(sum_array, columns=['x_cum', 'y_cum'])
        tmp = tmp.assign(x_cum=sum_df.x_cum.values,
                         y_cum=sum_df.y_cum.values)
        list_.append(tmp)

    result = pd.concat(list_)
    return result


def compute_displacements(df, id_, x_coord, y_coord):
    """Compute net displacements of motion in the two directions, x and y.

    df -- the trajectories dataframe
    id_ -- an identifier
    x_coord -- the x coordinate
    y_coord -- the y coordinate
    """
    list_ = []
    df = df.dropna()
    for i in df[id_].unique():
        tmp = df[df[id_] == i]
        # convert coordinates columns into numpy array
        array = tmp[[x_coord, y_coord]].values
        # substract rows
        diff_array = np.diff(array, axis=0)
        # need to insert NaN at the first position
        diff_array = np.insert(diff_array, [0], [np.NaN, np.NaN], axis=0)
        diff_df = pd.DataFrame(diff_array, columns=['delta_x', 'delta_y'])
        tmp = tmp.assign(delta_x=diff_df.delta_x.values,
                         delta_y=diff_df.delta_y.values)
        list_.append(tmp)
    result = pd.concat(list_)
    return result


def compute_turning_angle(df, id_):
    """Compute turning angles.

    df -- the trajectories dataframe
    id_ -- an identifier
    """
    list_ = []
    for i in df[id_].unique():
        tmp = df[df[id_] == i]
        array = tmp[['delta_x', 'delta_y']].values
        turning_angle = np.apply_along_axis(
            lambda x: math.atan2(x[0], x[1]), 1, array)

        ta_df = pd.DataFrame(turning_angle, columns=['ta'])
        tmp = tmp.assign(ta=ta_df.ta.values)
        list_.append(tmp)
    result = pd.concat(list_)
    return result


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

    sns.plt.savefig("turning_angles.png")
