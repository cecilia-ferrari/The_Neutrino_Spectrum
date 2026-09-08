"""Draw the Grand Unified Neutrino Spectrum at Earth."""

from PlotFuncs import TheNuSpectrum, MySaveFig

# Initialize the plot class
plot = TheNuSpectrum()

# Set up the figure and axes
fig, ax = plot.FigSetup()

# The GUNS model components of arXiv:1910.11878
plot.relic_neutrinos(ax)
plot.bbn_neutrinos(ax)
plot.solar_neutrinos(ax)
plot.terrestrial_neutrinos(ax)
plot.supernova_neutrinos(ax)
plot.atmospheric_neutrinos(ax)
plot.astrophysical_neutrinos(ax)
plot.cosmogenic_neutrinos(ax)

# Measurements from Borexino, SNO, KamLAND, IceCube and KM3NeT
plot.data(ax)

# Labels, credits and the experiment colour key
plot.annotate(ax)
plot.experiment_legend(ax)

# Save the figure
MySaveFig(fig, 'figures/The_Neutrino_Spectrum', pngsave=True)
