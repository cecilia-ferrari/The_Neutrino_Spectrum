"""Draw the Grand Unified Neutrino Spectrum at Earth: model plus measurements."""

from PlotFuncs import TheNuSpectrum, MySaveFig

plot = TheNuSpectrum()
fig, ax = plot.FigSetup()

# The GUNS model components of arXiv:1910.11878
plot.model(ax)

# Measurements from Borexino, SNO, KamLAND, Super-K, IceCube and KM3NeT
plot.data(ax)

# Diagonal guides for the integral rate through unit area
plot.iso_rate_lines(ax)

# Labels, credits and the experiment colour key
plot.annotate(ax)
plot.experiment_legend(ax)

MySaveFig(fig, 'figures/The_Neutrino_Spectrum', pngsave=True)
