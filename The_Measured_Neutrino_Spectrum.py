"""Only the measured neutrino fluxes -- no model curves.

Deliberately drawn on exactly the same axes, limits and aspect ratio as
``The_Neutrino_Spectrum.py``, so the two figures can be laid side by side and
what is measured can be read straight off against what is predicted.
"""

from PlotFuncs import TheNuSpectrum, MySaveFig

plot = TheNuSpectrum()
fig, ax = plot.FigSetup()

# Measurements only
plot.data(ax)

# The diagonals are reading guides, not spectra, so they stay
plot.iso_rate_lines(ax)

notes = [
    r'Measured neutrino fluxes only --- no model components are drawn',
    r'Stems are monochromatic lines: height is an \emph{integral} flux in '
    r'cm$^{-2}$ s$^{-1}$, offset down by $10^{6}$ for the solar ones',
    r'Dotted diagonals: rate above $E$ through unit area, '
    r'$N(>E) = E\,\Phi(E)$ for an $E^{-2}$ spectrum',
]
plot.annotate(ax, labels=plot.measured_labels,
              arrow_labels=plot.measured_arrow_labels,
              palette=plot.experiments, notes=notes)
plot.experiment_legend(ax)

MySaveFig(fig, 'figures/The_Measured_Neutrino_Spectrum', pngsave=True)
