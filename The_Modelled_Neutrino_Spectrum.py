"""Only the predicted neutrino fluxes -- no measurements.

The complement of ``The_Measured_Neutrino_Spectrum.py``, and on the same axes,
limits and aspect ratio as ``The_Neutrino_Spectrum.py``, so any pair of the
three can be laid side by side.  On its own it is a reproduction of Fig. 1 of
arXiv:1910.11878.
"""

from PlotFuncs import TheNuSpectrum, MySaveFig

plot = TheNuSpectrum()
fig, ax = plot.FigSetup()

# The GUNS model components only
plot.model(ax)

# The diagonals are reading guides, not spectra, so they stay
plot.iso_rate_lines(ax)

# No experiment legend: there is nothing measured on this figure.  The CEvNS
# footnote goes too, for the same reason.
notes = [r'Predicted fluxes only --- no measurements are drawn'] + plot.DEFAULT_NOTES[:3]
plot.annotate(ax, notes=notes)

MySaveFig(fig, 'figures/The_Modelled_Neutrino_Spectrum', pngsave=True)
