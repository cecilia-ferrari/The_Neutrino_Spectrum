"""Plotting machinery for the Grand Unified Neutrino Spectrum at Earth.

The layout follows C. Evoli's ``The_CR_Spectrum`` (github.com/carmeloevoli/
The_CR_Spectrum); the physics content follows

    E. Vitagliano, I. Tamborra, G. Raffelt,
    "Grand Unified Neutrino Spectrum at Earth",
    Rev. Mod. Phys. 92 (2020) 045006 [arXiv:1910.11878]

Everything is drawn from the plot-ready tables in ``data/output``, produced by
the scripts in ``data/``.

Three figures are built on this class:

    The_Neutrino_Spectrum.py           model + measurements  (the GUNS axes)
    The_Multimessenger_Spectrum.py     the above + cosmic rays (wider axes)
    The_Measured_Neutrino_Spectrum.py  measurements only     (the GUNS axes)
"""

import platform
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

if platform.system() == 'Darwin':
    matplotlib.use('Agg')

BASE_DIR = Path(__file__).resolve().parent
DATA_OUTPUT_DIR = BASE_DIR / 'data' / 'output'

plt.style.use(BASE_DIR / 'guns.mplstyle')

CREDIT_URL = 'github.com/cecilia-ferrari/The_Neutrino_Spectrum'


def MySaveFig(fig, pltname, pngsave=False):
    """Save a figure as pdf and, optionally, png."""
    if pngsave:
        fig.savefig(f'{pltname}.png', bbox_inches='tight', dpi=200)
        print(f'Saving plot as {pltname}.png')
    fig.savefig(f'{pltname}.pdf', bbox_inches='tight', dpi=200)
    print(f'Saving plot as {pltname}.pdf')


class TheNuSpectrum:
    """Draws the Grand Unified Neutrino Spectrum at Earth."""

    # Axis ranges of Fig. 1 of arXiv:1910.11878, read off the `Produce-your-GUNS`
    # Mathematica notebook shipped as ancillary material with the paper.
    GUNS_E_RANGE = (1.75e-7, 8.4e18)        # eV
    GUNS_PHI_RANGE = (1e-36, 1e18)          # eV^-1 cm^-2 s^-1

    # Widened just enough to hold the cosmic-ray spectrum as well, which reaches
    # 2.2e20 eV and 8.6e-41 eV^-1 cm^-2 s^-1.
    MULTIMESSENGER_E_RANGE = (1.75e-7, 1e21)
    MULTIMESSENGER_PHI_RANGE = (1e-42, 1e18)

    FIGSIZE = {'guns': (16.0, 12.5), 'multimessenger': (17.5, 14.0)}

    EV_TO_JOULE = 1.602176634e-19

    # Monochromatic components carry an *integral* flux in cm^-2 s^-1, which
    # cannot share a differential axis.  Following Fig. 1 of the paper, the solar
    # lines are drawn 6 decades below their true value so that they sit next to
    # the continua they belong to, while the CNB lines are drawn unscaled.
    SOLAR_LINE_DISPLAY_SCALE = 1e-6
    CNB_LINE_DISPLAY_SCALE = 1.0

    # Height of the vertical stem drawn under a monochromatic line, in decades.
    LINE_STEM_DECADES = 4.0

    # Colours of the model components.
    colors = {
        'CNB': '#1F4E9C',
        'BBN': '#7A3FA8',
        'solar_thermal': '#C77E23',
        'solar_nuclear': '#E4572E',
        'geoneutrinos': '#2E8B57',
        'reactor': '#00A0B0',
        'DSNB': '#B5179E',
        'atmospheric': '#0F7B8A',
        'astrophysical': '#8A2BE2',
        'cosmogenic': '#5A5A5A',
    }

    # Colours of the cosmic-ray species, kept in a separate dark/earthy family so
    # that the neutrinos stay the subject of the figure.
    cr_colors = {
        'allparticle': '#2B2B2B',
        'protons': '#8C510A',
        'leptons': '#BF812D',
    }

    # Colours of the experiments providing measured neutrino points.
    experiments = {
        'Borexino': '#F5A400',
        'SNO': '#00A651',
        'PandaX-4T': '#4169E1',
        'XENONnT': '#5B2C8D',
        'LZ': '#8B4513',
        'KamLAND': '#FF3DBE',
        'Super-K': '#D62728',
        'IceCube': '#8A2BE2',
        'KM3NeT': '#141E3C',
    }

    # Year of the measurement shown for each experiment, for the legend.
    experiment_years = {
        'Borexino': '2018--2023',
        'SNO': '2013',
        'PandaX-4T': '2024',
        'XENONnT': '2024',
        'LZ': '2025',
        'KamLAND': '2022',
        'Super-K': '2016, 2026',
        'IceCube': '2011--2026',
        'KM3NeT': '2025',
    }

    # Experiments quoting an integral flux, and the marker each is drawn with.
    # The three CEvNS results share a shape because they are the same kind of
    # measurement: a total, flavour-blind 8B flux.
    integral_markers = {
        'KamLAND': 'D',
        'Super-K': '*',
        'PandaX-4T': 'o',
        'XENONnT': 'o',
        'LZ': 'o',
    }

    # Where one colour carries several marker shapes, spell them out under the
    # entry: (marker, label) pairs, drawn left to right.
    experiment_markers = {
        'Super-K': [('o', r'$\nu_e$'), ('s', r'$\nu_\mu$'), ('v', r'DSNB')],
        'IceCube': [('^', r'atm.'), ('o', r'astro.')],
    }

    # Cosmetic truncation of the curves that end on a sharp kinematic edge: the
    # tabulated flux there plunges by tens of decades within one sample, which
    # renders as a spurious vertical line.  Only these components are clipped;
    # power-law tails (atmospheric, astrophysical) are never touched.
    display_floor = {
        'CNB_flux.txt': 1e2,
        'BBN_tritium_flux.txt': 1e-12,
        'BBN_neutron_flux.txt': 1e-12,
        'Geoneutrinos_flux.txt': 1e-3,
        'Cosmogenic_He_flux.txt': 1e-38,
        'Cosmogenic_Fe_flux.txt': 1e-38,
    }

    def __init__(self, axes='guns'):
        self.datadir = DATA_OUTPUT_DIR
        self.axes_kind = axes
        if axes == 'multimessenger':
            self.E_MIN, self.E_MAX = self.MULTIMESSENGER_E_RANGE
            self.PHI_MIN, self.PHI_MAX = self.MULTIMESSENGER_PHI_RANGE
        else:
            self.E_MIN, self.E_MAX = self.GUNS_E_RANGE
            self.PHI_MIN, self.PHI_MAX = self.GUNS_PHI_RANGE

    # ------------------------------------------------------------------ setup

    def FigSetup(self, shape='Rectangular'):
        figsize = self.FIGSIZE.get(self.axes_kind, self.FIGSIZE['guns'])
        if shape == 'Wide':
            figsize = (figsize[0] * 1.3, figsize[1] * 0.6)
        fig, ax = plt.subplots(figsize=figsize)
        self.SetAxes(ax)
        return fig, ax

    @staticmethod
    def _decade_ticks(lo, hi, step):
        """Ticks every `step` decades, aligned on multiples of `step`."""
        first = step * math_ceil(np.log10(lo) / step)
        last = step * math_floor(np.log10(hi) / step)
        return 10.0 ** np.arange(first, last + 1, step)

    def SetAxes(self, ax):
        ax.minorticks_off()
        ax.set_xscale('log')
        ax.set_xlim([self.E_MIN, self.E_MAX])
        ax.set_xticks(self._decade_ticks(self.E_MIN, self.E_MAX, 2))
        ax.set_xlabel(r'Neutrino energy [eV]' if self.axes_kind != 'multimessenger'
                      else r'Energy [eV]')

        ax.set_yscale('log')
        ax.set_ylim([self.PHI_MIN, self.PHI_MAX])
        ax.set_yticks(self._decade_ticks(self.PHI_MIN, self.PHI_MAX, 6))
        ylabel = ('Flux' if self.axes_kind == 'multimessenger' else 'Neutrino flux')
        ax.set_ylabel(ylabel + r' [eV$^{-1}$ cm$^{-2}$ s$^{-1}$]')

        ax2 = ax.twiny()
        ax2.minorticks_off()
        ax2.set_xscale('log')
        j_lo, j_hi = self.E_MIN * self.EV_TO_JOULE, self.E_MAX * self.EV_TO_JOULE
        ax2.set_xlim([j_lo, j_hi])
        ax2.set_xticks(self._decade_ticks(j_lo, j_hi, 2))
        ax2.set_xlabel(r'Energy [J]', color='tab:blue', labelpad=16)
        ax2.tick_params(axis='x', colors='tab:blue')

    # ------------------------------------------------------------- data input

    def load(self, filename):
        """Load a plot-ready table from ``data/output``."""
        return np.loadtxt(self.datadir / filename, comments='#', unpack=True, ndmin=2)

    # ------------------------------------------------------- drawing helpers

    def _clean(self, filename, E, *fluxes):
        """Drop what cannot be shown on a log axis, and apply the display floor."""
        floor = max(self.display_floor.get(filename, 0.0), self.PHI_MIN)
        good = np.isfinite(E) & (E > 0.0)
        for phi in fluxes:
            good &= np.isfinite(phi) & (phi > floor)
        return [E[good]] + [phi[good] for phi in fluxes]

    def plot_line(self, ax, filename, color, ls='-', lw=2.5, zorder=1, alpha=1.0):
        E, phi = self.load(filename)[:2]
        E, phi = self._clean(filename, E, phi)
        ax.plot(E, phi, color=color, ls=ls, lw=lw, zorder=zorder, alpha=alpha)

    def plot_band(self, ax, filename, color, zorder=1, alpha=0.35, lw=1.6):
        E, lo, up = self.load(filename)[:3]
        E, lo, up = self._clean(filename, E, lo, up)
        ax.fill_between(E, lo, up, facecolor=color, edgecolor=color,
                        lw=lw, alpha=alpha, zorder=zorder)
        ax.plot(E, up, color=color, lw=lw, zorder=zorder)

    def plot_spectral_lines(self, ax, filename, color, scale, zorder=1):
        """Monochromatic model components, drawn as a bare stem.

        The stem top is the value; no marker is added, so that markers on this
        figure always mean a measurement.  ``scale`` is the display scale defined
        above -- the tables themselves hold physical integral fluxes in
        cm^-2 s^-1.
        """
        table = self.load(filename)
        E, phi = table[0], table[1] * scale
        for E_, phi_ in zip(E, phi):
            ax.plot([E_, E_], [phi_ / 10 ** self.LINE_STEM_DECADES, phi_],
                    color=color, lw=2.5, zorder=zorder, solid_capstyle='butt')

    def plot_measured_lines(self, ax, filename, color, scale, zorder=1, marker='s'):
        """Measured integral fluxes, with their error bars."""
        table = self.load(filename)
        E = table[0]
        phi, dlo, dup = table[1] * scale, table[2] * scale, table[3] * scale
        ax.errorbar(E, phi, yerr=[dlo, dup], ls='none', marker=marker, ms=11,
                    color=color, markeredgecolor=color, markerfacecolor='white',
                    markeredgewidth=2.0, elinewidth=2.0, capsize=4, zorder=zorder)

    def plot_points(self, ax, filename, color, zorder=1, marker='o', ms=8):
        """Differential measurements; bins with a null upper error are upper limits."""
        E, dElo, dEup, phi, dlo, dup = self.load(filename)[:6]

        limits = dup <= 0.0
        if np.any(~limits):
            m = ~limits
            ax.errorbar(E[m], phi[m], xerr=[dElo[m], dEup[m]], yerr=[dlo[m], dup[m]],
                        ls='none', marker=marker, ms=ms, color=color,
                        markeredgecolor=color, elinewidth=2.0, capsize=0,
                        zorder=zorder)
        if np.any(limits):
            m = limits
            ax.errorbar(E[m], phi[m], xerr=[dElo[m], dEup[m]],
                        yerr=[dlo[m], np.zeros(m.sum())], ls='none',
                        marker='v', ms=ms, color=color, markeredgecolor=color,
                        markerfacecolor='white', elinewidth=1.6,
                        uplims=True, zorder=zorder)

    # -------------------------------------------------------- the components

    def relic_neutrinos(self, ax):
        c = self.colors['CNB']
        self.plot_line(ax, 'CNB_flux.txt', c, zorder=10)
        self.plot_spectral_lines(ax, 'CNB_lines.txt', c,
                                 self.CNB_LINE_DISPLAY_SCALE, zorder=11)

    def bbn_neutrinos(self, ax):
        c = self.colors['BBN']
        self.plot_line(ax, 'BBN_tritium_flux.txt', c, zorder=9)
        self.plot_line(ax, 'BBN_neutron_flux.txt', c, ls='--', zorder=9)

    def solar_neutrinos(self, ax):
        thermal, nuclear = self.colors['solar_thermal'], self.colors['solar_nuclear']
        self.plot_line(ax, 'Sun_thermal_flux.txt', thermal, zorder=8)
        self.plot_line(ax, 'Sun_pp_flux.txt', nuclear, zorder=12)
        self.plot_line(ax, 'Sun_B8_flux.txt', nuclear, zorder=12)
        self.plot_band(ax, 'Sun_hep_band.txt', nuclear, zorder=12)
        self.plot_band(ax, 'Sun_CNO_band.txt', nuclear, zorder=12)
        self.plot_spectral_lines(ax, 'Sun_lines.txt', nuclear,
                                 self.SOLAR_LINE_DISPLAY_SCALE, zorder=13)

    def terrestrial_neutrinos(self, ax):
        self.plot_line(ax, 'Geoneutrinos_flux.txt', self.colors['geoneutrinos'], zorder=7)
        self.plot_line(ax, 'Reactor_flux.txt', self.colors['reactor'], zorder=7)

    def supernova_neutrinos(self, ax):
        c = self.colors['DSNB']
        self.plot_band(ax, 'DSNB_nu_band.txt', c, zorder=6)
        self.plot_band(ax, 'DSNB_antinu_band.txt', c, zorder=6, alpha=0.2)

    def atmospheric_neutrinos(self, ax):
        c = self.colors['atmospheric']
        self.plot_line(ax, 'Atmospheric_nu_flux.txt', c, zorder=6)
        self.plot_line(ax, 'Atmospheric_antinu_flux.txt', c, ls='--', zorder=6)

    def astrophysical_neutrinos(self, ax):
        self.plot_band(ax, 'IceCube2017_band.txt', self.colors['astrophysical'],
                       zorder=6, alpha=0.5)

    def cosmogenic_neutrinos(self, ax):
        c = self.colors['cosmogenic']
        self.plot_line(ax, 'Cosmogenic_He_flux.txt', c, zorder=5)
        self.plot_line(ax, 'Cosmogenic_Fe_flux.txt', c, ls='--', zorder=5)

    def model(self, ax):
        """All the GUNS model components of arXiv:1910.11878."""
        self.relic_neutrinos(ax)
        self.bbn_neutrinos(ax)
        self.solar_neutrinos(ax)
        self.terrestrial_neutrinos(ax)
        self.supernova_neutrinos(ax)
        self.atmospheric_neutrinos(ax)
        self.astrophysical_neutrinos(ax)
        self.cosmogenic_neutrinos(ax)

    # ------------------------------------------------------------------ data

    def data(self, ax):
        """Measurements from the experiments discussed in the paper."""
        # The measured bands go *under* the model curves, so that the shading
        # reads as the measurement and the line on top as the GUNS prediction.
        self.plot_band(ax, 'Borexino_pp_band.txt', self.experiments['Borexino'],
                       zorder=4, alpha=0.75, lw=3.0)
        self.plot_band(ax, 'Borexino_CNO_band.txt', self.experiments['Borexino'],
                       zorder=4, alpha=0.75, lw=3.0)
        self.plot_band(ax, 'SNO_B8_band.txt', self.experiments['SNO'],
                       zorder=4, alpha=0.75, lw=3.0)
        self.plot_measured_lines(ax, 'Measured_lines.txt', self.experiments['Borexino'],
                                 self.SOLAR_LINE_DISPLAY_SCALE, zorder=16)
        for experiment, marker in self.integral_markers.items():
            self.plot_measured_lines(
                ax, f'Measured_integrals_{experiment}.txt',
                self.experiments[experiment], self.SOLAR_LINE_DISPLAY_SCALE,
                zorder=16, marker=marker)

        # Atmospheric spectra: Super-K measures nu_e (circles) and nu_mu
        # (squares); the IceCube unfolding (triangles) is nu_mu only.
        self.plot_points(ax, 'SuperK_atm_nue_points.txt',
                         self.experiments['Super-K'], zorder=16, marker='o')
        self.plot_points(ax, 'SuperK_atm_numu_points.txt',
                         self.experiments['Super-K'], zorder=16, marker='s')
        self.plot_points(ax, 'IceCube_atm_numu_points.txt',
                         self.experiments['IceCube'], zorder=16, marker='^')

        # Super-K DSNB: published 90% C.L. upper limits (drawn as open
        # down-arrows by plot_points, since their upper error is null).
        self.plot_points(ax, 'SuperK_DSNB_limits_points.txt',
                         self.experiments['Super-K'], zorder=16)

        self.plot_points(ax, 'IceCube_combinedfit_points.txt',
                         self.experiments['IceCube'], zorder=17)
        self.plot_points(ax, 'IceCube_mese_points.txt',
                         self.experiments['IceCube'], zorder=17, marker='s')
        self.plot_points(ax, 'IceCube_glashow_points.txt',
                         self.experiments['IceCube'], zorder=17, marker='*')
        self.plot_points(ax, 'KM3NeT_km3_230213A_points.txt',
                         self.experiments['KM3NeT'], zorder=18, marker='D')

    def cosmic_rays(self, ax):
        """Charged cosmic rays, from the KISS tables behind The_CR_Spectrum."""
        self.plot_points(ax, 'CR_allparticle_points.txt',
                         self.cr_colors['allparticle'], zorder=14, marker='o', ms=5)
        self.plot_points(ax, 'CR_protons_points.txt',
                         self.cr_colors['protons'], zorder=14, marker='s', ms=4)
        self.plot_points(ax, 'CR_leptons_points.txt',
                         self.cr_colors['leptons'], zorder=14, marker='^', ms=4)

    # ------------------------------------------------------------ decoration

    # text, x [eV], y [flux], colour key, font size
    labels = [
        (r'C$\nu$B', 3.0e-4, 2.0e16, 'CNB', 20),
        (r'$n$', 4.0e-5, 3.0e6, 'BBN', 18),
        (r'$^3$H', 4.0e-3, 2.0e-6, 'BBN', 18),
        (r'Solar (thermal)', 5.0e0, 3.0e4, 'solar_thermal', 18),
        (r'$pp$', 7.0e4, 1.5e7, 'solar_nuclear', 18),
        (r'$^7$Be', 1.1e6, 2.0e6, 'solar_nuclear', 18),
        (r'$pep$', 3.2e6, 1.2e4, 'solar_nuclear', 18),
        (r'$^8$B', 3.0e7, 3.0e-1, 'solar_nuclear', 18),
        (r'hep', 1.3e8, 2.0e-3, 'solar_nuclear', 18),
        (r'DSNB', 1.1e8, 5.0e-6, 'DSNB', 18),
        (r'Atmospheric', 8.0e9, 5.0e-9, 'atmospheric', 18),
        (r'Astrophysical', 1.5e15, 3.0e-22, 'astrophysical', 18),
        (r'Cosmogenic', 3.5e17, 2.0e-31, 'cosmogenic', 18),
    ]

    # Components buried in the crowded 10 keV - 10 MeV region get a leader line:
    # text, x_text, y_text, x_tip, y_tip, colour key
    arrow_labels = [
        (r'CNO', 1.2e2, 2.5e0, 2.0e4, 1.6e0, 'solar_nuclear'),
        (r'Geoneutrinos', 5.0e4, 6.0e-7, 1.5e5, 2.0e1, 'geoneutrinos'),
        (r'Reactors', 5.0e7, 5.0e2, 4.0e6, 6.0e-1, 'reactor'),
    ]

    # Labels for the measurements-only figure, coloured by experiment.
    measured_labels = [
        (r'$pp$', 7.0e4, 1.5e7, 'Borexino', 18),
        (r'$^7$Be', 1.1e6, 2.0e6, 'Borexino', 18),
        (r'$pep$', 3.2e6, 1.2e4, 'Borexino', 18),
        (r'CNO', 4.0e3, 5.0e1, 'Borexino', 18),
        (r'$^8$B', 3.0e7, 3.0e-1, 'SNO', 18),
        (r'DSNB', 8.0e7, 1.0e-5, 'Super-K', 18),
        (r'Atmospheric', 8.0e9, 5.0e-9, 'Super-K', 18),
        (r'Astrophysical', 1.5e15, 3.0e-22, 'IceCube', 18),
        (r'KM3-230213A', 3.0e17, 3.0e-31, 'KM3NeT', 16),
    ]

    # The KamLAND point sits in the middle of the solar cluster, so it gets a
    # leader line on the measurements-only figure.
    measured_arrow_labels = [
        (r'Geoneutrinos', 2.5e5, 3.0e-4, 2.15e6, 3.0, 'KamLAND'),
    ]

    # Cosmic-ray labels for the multimessenger figure.
    cr_labels = [
        (r'Cosmic rays', 7.0e15, 1.0e-24, 'allparticle', 18),
        (r'CR protons', 5.0e11, 3.0e-13, 'protons', 18),
        (r'CR $e^-\!+\!e^+$', 1.3e9, 2.0e-14, 'leptons', 18),
    ]

    # On the multimessenger figure these two neutrino labels fall inside the
    # cosmic-ray tracks, so they move into clear space and gain leader lines.
    MM_RELABELLED = ('Astrophysical', 'Cosmogenic')
    mm_arrow_labels = [
        (r'Astrophysical', 2.0e12, 2.0e-31, 3.0e14, 2.0e-27, 'astrophysical'),
        (r'Cosmogenic', 3.0e13, 2.0e-35, 3.0e16, 2.0e-32, 'cosmogenic'),
    ]

    # Diagonal guide lines marking how many particles above E cross unit area
    # per unit time.  For a spectrum falling as E^-gamma,
    #
    #     N(>E) = int_E^inf Phi dE' = E * Phi(E) / (gamma - 1),
    #
    # so a fixed rate is a straight line of slope -1 on these log-log axes.  We
    # draw them for gamma = 2, i.e. simply N(>E) = E * Phi(E); for any other
    # slope the reading is off by the factor (gamma - 1), of order unity.
    #   label, rate in cm^-2 s^-1
    SECONDS_PER_YEAR = 3.156e7
    iso_rates = [
        (r'1/$\mu$m$^2$/ms', 1e8 * 1e3),
        (r'1/$\mu$m$^2$/s', 1e8),
        (r'1/cm$^2$/s', 1e0),
        (r'1/m$^2$/s', 1e-4),
        (r'1/m$^2$/yr', 1e-4 / SECONDS_PER_YEAR),
        (r'1/km$^2$/yr', 1e-10 / SECONDS_PER_YEAR),
    ]

    # All labels are stacked on this vertical, in the empty left half.
    ISO_RATE_LABEL_X = 3.0e2

    def iso_rate_lines(self, ax, color='tab:gray'):
        fig = ax.get_figure()
        fig.canvas.draw()   # settle the layout before measuring the on-screen slope

        E = np.array([self.E_MIN, self.E_MAX])
        # Every line has slope -1 in log-log, so one angle serves them all.
        pts = ax.transData.transform(np.column_stack([E, 1.0 / E]))
        angle = np.degrees(np.arctan2(pts[1, 1] - pts[0, 1], pts[1, 0] - pts[0, 0]))

        x = self.ISO_RATE_LABEL_X
        for label, rate in self.iso_rates:
            ax.plot(E, rate / E, ls=':', lw=1.5, color=color, alpha=0.85, zorder=1)
            ax.text(x, rate / x, label, color=color, fontsize=14, rotation=angle,
                    ha='center', va='center', zorder=2,
                    bbox=dict(boxstyle='square,pad=0.12', fc='white', ec='none',
                              alpha=0.85))

    DEFAULT_NOTES = [
        r'Model components: Vitagliano, Tamborra \& Raffelt, '
        r'Rev.\ Mod.\ Phys.\ 92 (2020) 045006 [arXiv:1910.11878]',
        r'Stems are monochromatic lines: height is an \emph{integral} flux in '
        r'cm$^{-2}$ s$^{-1}$, offset down by $10^{6}$ for the solar ones',
        r'Dotted diagonals: rate above $E$ through unit area, '
        r'$N(>E) = E\,\Phi(E)$ for an $E^{-2}$ spectrum',
        r'PandaX-4T, XENONnT and LZ measure the \emph{total} $^8$B flux via '
        r'CE$\nu$NS; their points are spread in energy only for legibility',
        r'Super-K DSNB: open triangles are 90\% C.L.\ upper limits '
        r'[arXiv:2511.02222]; the star is the \emph{preliminary} '
        r'2.6$\sigma$ indication shown at Neutrino 2026',
    ]

    def annotate(self, ax, labels=None, arrow_labels=None, notes=None,
                 palette=None):
        """Draw the component labels, leader lines and footnotes.

        ``palette`` maps a label's colour key to a colour; it defaults to the
        model colours, and the measurements-only figure passes the experiment
        colours instead.
        """
        palette = palette if palette is not None else self.colors
        labels = self.labels if labels is None else labels
        arrow_labels = self.arrow_labels if arrow_labels is None else arrow_labels
        notes = self.DEFAULT_NOTES if notes is None else notes

        for text, x, y, key, size in labels:
            ax.text(x, y, text, color=palette[key], fontsize=size,
                    zorder=25, ha='center', va='center')

        for text, xt, yt, x, y, key in arrow_labels:
            ax.annotate(text, xy=(x, y), xytext=(xt, yt), color=palette[key],
                        fontsize=18, zorder=25, ha='center', va='center',
                        arrowprops=dict(arrowstyle='->', color=palette[key],
                                        lw=1.3, shrinkA=6, shrinkB=3))

        for i, note in enumerate(notes):
            ax.text(0.013, 0.135 - 0.022 * i, note, transform=ax.transAxes,
                    fontsize=13, color='tab:gray', zorder=25, va='bottom')

        ax.text(1.012, 0.5, CREDIT_URL, transform=ax.transAxes, rotation=-90,
                fontsize=12, color='tab:gray', ha='left', va='center', zorder=25)

    def experiment_legend(self, ax, x=0.985, y=0.945, dy=0.033):
        """Colour key of the measurements, in the style of The_CR_Spectrum.

        Experiments whose colour carries more than one marker shape get a second
        line spelling the shapes out, drawn with the real markers.
        """
        ax.text(x, y, r'Measurements', transform=ax.transAxes,
                color='black', fontsize=17, ha='right', zorder=25)

        row = y
        for name, color in self.experiments.items():
            row -= dy
            entry = f'{name} ({self.experiment_years[name]})'
            ax.text(x, row, entry, transform=ax.transAxes, color=color,
                    fontsize=16, ha='right', zorder=25)

            pairs = self.experiment_markers.get(name)
            if not pairs:
                continue

            # Sub-line: fixed slots filled right to left, each holding a marker
            # followed by its label, so the run ends flush under the entry above.
            row -= dy * 0.80
            slot, gap = 0.085, 0.016
            n = len(pairs)
            for i, (marker, label) in enumerate(pairs):
                x_marker = x - (n - i) * slot + 0.012
                # A down-triangle always means an upper limit here, and those
                # are drawn open on the figure, so the key matches.
                face = 'white' if marker == 'v' else color
                ax.plot([x_marker], [row + 0.005], transform=ax.transAxes,
                        marker=marker, ms=7, color=color, markeredgecolor=color,
                        markerfacecolor=face, ls='none', clip_on=False,
                        zorder=25)
                ax.text(x_marker + gap, row, label, transform=ax.transAxes,
                        color=color, fontsize=13, ha='left', va='baseline',
                        zorder=25)

    def cosmic_ray_legend(self, ax, x=0.985, y=0.44, dy=0.033):
        """Colour key of the cosmic-ray species, under the neutrino legend."""
        ax.text(x, y, r'Cosmic rays', transform=ax.transAxes,
                color='black', fontsize=17, ha='right', zorder=25)
        entries = [('allparticle', 'all particle'), ('protons', 'protons'),
                   ('leptons', r'$e^-\!+\!e^+$')]
        for i, (key, label) in enumerate(entries):
            ax.text(x, y - dy * (i + 1), label, transform=ax.transAxes,
                    color=self.cr_colors[key], fontsize=16, ha='right', zorder=25)


def math_ceil(v):
    return int(np.ceil(v))


def math_floor(v):
    return int(np.floor(v))
