"""The neutrino spectrum with the charged cosmic rays overlaid.

Same content as ``The_Neutrino_Spectrum.py``, plus the cosmic-ray data behind
carmeloevoli/The_CR_Spectrum.  The axes are widened to 10^21 eV and down to
10^-42 eV^-1 cm^-2 s^-1 so that the ultra-high-energy end of the cosmic-ray
spectrum fits.
"""

from PlotFuncs import TheNuSpectrum, MySaveFig

plot = TheNuSpectrum(axes='multimessenger')
fig, ax = plot.FigSetup()

plot.model(ax)
plot.data(ax)
plot.cosmic_rays(ax)
plot.iso_rate_lines(ax)

notes = plot.DEFAULT_NOTES + [
    r'Cosmic rays from the KISS tables behind \texttt{carmeloevoli/The\_CR\_Spectrum}; '
    r'these are particle fluxes, while each neutrino curve is a single species',
]
labels = [l for l in plot.labels if l[0] not in plot.MM_RELABELLED] + plot.cr_labels
plot.annotate(ax, labels=labels,
              arrow_labels=plot.arrow_labels + plot.mm_arrow_labels,
              palette={**plot.colors, **plot.cr_colors}, notes=notes)
plot.experiment_legend(ax)
plot.cosmic_ray_legend(ax)

MySaveFig(fig, 'figures/The_Multimessenger_Spectrum', pngsave=True)
