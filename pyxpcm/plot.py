#!/bin/env python
# -*coding: UTF-8 -*-
#
# Provide some basic methods for plotting
#
# Created by gmaze on 2017/12/11
__author__ = 'gmaze@ifremer.fr'

import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.cm as cm
import matplotlib.colors as mcolors
from sklearn.utils import validation

def cmap_robustess():
    """ Return a categorical colormap for robustness """
    return mpl.colors.ListedColormap(['#FF0000', '#CC00FF', '#0066FF', '#CCFF00', '#00FF66'])

def cmap_discretize(name, K):
    """Return a discrete colormap from a quantitative or continuous colormap name

        name: name of the colormap, eg 'Paired' or 'jet'
        K: number of colors in the final discrete colormap
    """
    if name in ['Set1','Set2','Set3','Pastel1','Pastel2','Paired','Dark2','Accent']:
        # Segmented (or quantitative) colormap:
        N_ref = {'Set1':9,'Set2':8,'Set3':12,'Pastel1':9,'Pastel2':8,'Paired':12,'Dark2':8,'Accent':8}
        N = N_ref[name]
        cmap = plt.get_cmap(name=name)
        colors_i = np.concatenate((np.linspace(0, 1., N), (0., 0., 0., 0.)), axis=0)
        cmap = cmap(colors_i) # N x 4
        n = np.arange(0, N)
        new_n = n.copy()
        if K>N:
            for k in range(N,K):
                r = np.roll(n,-k)[0][np.newaxis]
                r[3] = 0.5
                new_n = np.concatenate((new_n, r), axis=0)
        new_cmap = cmap.copy()
        new_cmap = cmap[new_n,:]
        new_cmap = mcolors.LinearSegmentedColormap.from_list(name + "_%d" % K, colors = new_cmap, N=K)
    else:
        # Continuous colormap:
        N = K
        cmap = plt.get_cmap(name=name)
        colors_i = np.concatenate((np.linspace(0, 1., N), (0., 0., 0., 0.)))
        colors_rgba = cmap(colors_i) # N x 4
        indices = np.linspace(0, 1., N + 1)
        cdict = {}
        for ki, key in enumerate(('red', 'green', 'blue')):
            cdict[key] = [(indices[i], colors_rgba[i - 1, ki], colors_rgba[i, ki])
                          for i in np.arange(N + 1)]
        # Return colormap object.
        new_cmap = mcolors.LinearSegmentedColormap(cmap.name + "_%d" % N, cdict, N)
    return new_cmap

def colorbar_index(ncolors, cmap, **kwargs):
    """Adjust colorbar ticks with discrete colors"""
    cmap = cmap_discretize(cmap, ncolors)
    mappable = cm.ScalarMappable(cmap=cmap)
    mappable.set_array([])
    mappable.set_clim(-0.5, ncolors+0.5)
    colorbar = plt.colorbar(mappable, **kwargs)
    colorbar.set_ticks(np.linspace(0, ncolors, ncolors))
    colorbar.set_ticklabels(range(ncolors))
    return colorbar

def plot(m, type=None, ax=None, subplot_kws=None, **kwargs):
    if type == 'scaler':
        return scaler(m, ax=ax, subplot_kws=subplot_kws, **kwargs)
    else:
        print('You can plot the scaler properties using pcm.plot.scaler()')

class _PlotMethods(object):
    """
        Enables use of pyxpcm.plot functions as attributes on a PCM object.
        For example: m.plot(), m.plot.scaler(), m.plot.cmap('Jet'), m.plot.colorbar()
    """

    def __init__(self, m):
        self._pcm = m
        self._cmap = self.cmap()

    def __call__(self, **kwargs):
        return plot(self._pcm, **kwargs)

    def cmap(self, name='Set2'):
        """Return categorical colormap for this PCM"""
        self._cmap = cmap_discretize(name, self._pcm.K)
        return self._cmap

    def colorbar(self, cmap=None, **kwargs):
        """Add a colorbar to current plot with centered ticks on discrete colors"""
        if cmap==None:
            cmap=self._cmap
        z = { **{'fraction':0.03, 'label':'Class'}, **kwargs}
        return colorbar_index(ncolors=self._pcm.K, cmap=cmap, **z)

    def scaler(self, **kwargs):
        """Plot PCM scaler properties"""
        return plot(self._pcm, type='scaler', **kwargs)

def scaler(m, ax=None, subplot_kws=None, **kwargs):
    """Plot the scaler properties

    Parameters
    ----------
    m: PCM class instance

    """
    # Check if the PCM is trained:
    validation.check_is_fitted(m, 'fitted')

    fig, ax = plt.subplots(nrows=m.F, ncols=2, sharey='row', figsize=(10, 5), dpi=80, facecolor='w', edgecolor='k')
    if m.F==1:
        ax = ax[np.newaxis,:]

    for (feature, irow) in zip(m._props['features'], np.arange(0, m.F)):
        X_ave = m._scaler[feature].mean_
        X_std = m._scaler[feature].scale_
        X_unit = m._scaler_props[feature]['units']
        feature_axis = m._props['features'][feature]
        feature_name = [feature]

        ax[irow, 0].plot(X_ave, feature_axis, '-', linewidth=2, label='Sample Mean')
        ax[irow, 1].plot(X_std, feature_axis, '-', linewidth=2, label='Sample Std')
        # tidy up the figure
        ax[irow, 0].set_ylabel('Feature axis')
        for ix in range(0, 2):
            ax[irow, ix].legend(loc='lower right')
            ax[irow, ix].grid(True)
            ax[irow, ix].set_xlabel("[%s]" % X_unit)
            ax[irow, ix].set_title("%s scaler" % feature, fontsize=10)
    plt.show()

def quant(m, da, xlim=None, classdimname='N_CLASS'):
    """Plot the q-th quantiles of a dataArray for each PCM component

    Parameters
    ----------
    m: PCM class instance

    da: :class:`xarray.DataArray` with quantiles

    Returns
    -------
    fig : :class:`matplotlib.pyplot.figure.Figure`

    ax : :class:`matplotlib.axes.Axes` object or array of Axes objects.
        *ax* can be either a single :class:`matplotlib.axes.Axes` object or an
        array of Axes objects if more than one subplot was created.  The
        dimensions of the resulting array can be controlled with the squeeze
        keyword, see above.
    """

    # Check if the PCM is trained:
    validation.check_is_fitted(m, 'fitted')

    # da must be 3D with a dimension for: CLASS, QUANTILES and a vertical axis
    # The QUANTILES dimension is called "quantile"
    # The CLASS dimension is identified as the one matching m.K length.
    if classdimname in da.dims:
        CLASS_DIM = classdimname
    elif (np.argwhere(np.array(da.shape) == m.K).shape[0] > 1):
        raise ValueError("Can't distinguish the class dimension from the others")
    else:
        CLASS_DIM = da.dims[np.argwhere(np.array(da.shape) == m.K)[0][0]]
    QUANT_DIM = 'quantile'
    VERTICAL_DIM = list(set(da.dims) - set([CLASS_DIM]) - set([QUANT_DIM]))[0]

    nQ = len(da[QUANT_DIM]) # Nb of quantiles
    cmapK = cmap_discretize(plt.cm.get_cmap(name='Paired'), m.K)
    cmapQ = cmap_discretize(plt.cm.get_cmap(name='brg'), nQ)
    fig, ax = plt.subplots(nrows=1, ncols=m.K, figsize=(2 * m.K, 4), dpi=80, facecolor='w', edgecolor='k', sharey='row')
    if not xlim:
        xlim = np.array([0.9 * da.min(), 1.1 * da.max()])
    for k in m:
        # Qk = da.sel(CLASS_DIM=k)
        Qk = da.loc[{CLASS_DIM:k}]
        for (iq, q) in zip(np.arange(nQ), Qk[QUANT_DIM]):
            Qkq = Qk.loc[{QUANT_DIM:q}]
            ax[k].plot(Qkq.values.T, da[VERTICAL_DIM], label=("%0.2f") % (Qkq[QUANT_DIM]), color=cmapQ(iq))
        ax[k].set_title(("Component: %i") % (k), color=cmapK(k))
        ax[k].legend(loc='lower right')
        ax[k].set_xlim(xlim)
        ax[k].set_ylim(np.array([da[VERTICAL_DIM].min(), da[VERTICAL_DIM].max()]))
        # ax[k].set_xlabel(Q.units)
        if k == 0: ax[k].set_ylabel('feature dimension')
        ax[k].grid(True)
    plt.tight_layout()

    return fig, ax
