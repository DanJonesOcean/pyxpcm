.. Generate API reference pages, but don't display these in tables.
.. This extra page is a work around for sphinx not having any support for
.. hiding an autosummary table.

.. currentmodule:: pyxpcm

.. autosummary::
    :toctree: generated/

    pcmodel.pcm
    pcmodel.pcm.K
    pcmodel.pcm.F
    pcmodel.pcm.features
    pcmodel.pcm.scaler
    pcmodel.pcm.timeit
    pcmodel.pcm.fit
    pcmodel.pcm.fit_predict
    pcmodel.pcm.predict
    pcmodel.pcm.predict_proba
    pcmodel.pcm.score
    pcmodel.pcm.bic

    pcmodel.pcm.plot
    pcmodel.pcm.plot.cmap
    pcmodel.pcm.plot.colorbar
    pcmodel.pcm.plot.subplots
    pcmodel.pcm.plot.scaler
    pcmodel.pcm.plot.reducer
    pcmodel.pcm.plot.timeit
    pcmodel.pcm.plot.preprocessed
    pcmodel.pcm.plot.quantile

    plot.cmap_robustness
    plot.latlongrid
    plot.scaler
    plot.reducer
    plot.quantile

    tutorial.open_dataset

    ds_pyxpcm.add
    ds_pyxpcm.clean
    ds_pyxpcm.feature_dict
    ds_pyxpcm.sampling_dim
    ds_pyxpcm.mask
    ds_pyxpcm.quantile
    ds_pyxpcm.robustness
    ds_pyxpcm.robustness_digit
    ds_pyxpcm.fit
    ds_pyxpcm.fit_predict
    ds_pyxpcm.predict
    ds_pyxpcm.predict_proba
    ds_pyxpcm.score
    ds_pyxpcm.bic