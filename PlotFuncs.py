"""Plotting machinery for the Grand Unified Neutrino Spectrum at Earth.

The layout follows C. Evoli's ``The_CR_Spectrum`` (github.com/carmeloevoli/
The_CR_Spectrum); the physics content follows

    E. Vitagliano, I. Tamborra, G. Raffelt,
    "Grand Unified Neutrino Spectrum at Earth",
    Rev. Mod. Phys. 92 (2020) 045006 [arXiv:1910.11878]

Everything is drawn from the plot-ready tables in ``data/output``, produced by
the scripts in ``data/``.
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
    E_MIN, E_MAX = 1.75e-7, 8.4e18          # eV
    PHI_MIN, PHI_MAX = 1e-36, 1e18          # eV^-1 cm^-2 s^-1

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

    # Year of the measurement shown for each experiment, for the legend.
    experiment_years = {
        'Borexino': '2018--2023',
        'SNO': '2013',
        'KamLAND': '2022',
        'Super-K': '2016',
        'IceCube': '2011--2026',
        'KM3NeT': '2025',
    }

    # Colours of the experiments providing measured points.
    experiments = {
        'Borexino': '#F5A400',
        'SNO': '#00A651',
        'KamLAND': '#FF3DBE',
        'Super-K': '#D62728',
        'IceCube': '#8A2BE2',
        'KM3NeT': '#141E3C',
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

    def __init__(self):
        self.datadir = DATA_OUTPUT_DIR

    # ------------------------------------------------------------------ setup

    def FigSetup(self, shape='Rectangular'):
        figsize = (22.0, 8.0) if shape == 'Wide' else (16.0, 12.5)
        fig, ax = plt.subplots(figsize=figsize)
        self.SetAxes(ax)
        return fig, ax

    def SetAxes(self, ax):
        ax.minorticks_off()
        ax.set_xscale('log')
        ax.set_xlim([self.E_MIN, self.E_MAX])
        ax.set_xticks(np.logspace(-6, 18, 13))
        ax.set_xlabel(r'Neutrino energy [eV]')

        ax.set_yscale('log')
        ax.set_ylim([self.PHI_MIN, self.PHI_MAX])
        ax.set_yticks(np.logspace(-36, 18, 10))
        ax.set_ylabel(r'Neutrino flux [eV$^{-1}$ cm$^{-2}$ s$^{-1}$]')

        ax2 = ax.twiny()
        ax2.minorticks_off()
        ax2.set_xscale('log')
        ax2.set_xlim([self.E_MIN * self.EV_TO_JOULE, self.E_MAX * self.EV_TO_JOULE])
        ax2.set_xticks(np.logspace(-25, -1, 13))
        ax2.set_xlabel(r'Neutrino energy [J]', color='tab:blue', labelpad=16)
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

    def plot_spectral_lines(self, ax, filename, color, scale, zorder=1, marker='o'):
        """Monochromatic components: a stem topped by a marker.

        ``scale`` is the display scale defined above; the tables themselves hold
        physical integral fluxes in cm^-2 s^-1.
        """
        table = self.load(filename)
        E, phi = table[0], table[1] * scale
        for E_, phi_ in zip(E, phi):
            ax.plot([E_, E_], [phi_ / 10 ** self.LINE_STEM_DECADES, phi_],
                    color=color, lw=2.5, zorder=zorder, solid_capstyle='butt')
        ax.plot(E, phi, ls='none', marker=marker, ms=9, color=color,
                markeredgecolor=color, zorder=zorder + 1)

    def plot_measured_lines(self, ax, filename, color, scale, zorder=1, marker='s'):
        """Measured integral fluxes, with their error bars."""
        table = self.load(filename)
        E = table[0]
        phi, dlo, dup = table[1] * scale, table[2] * scale, table[3] * scale
        ax.errorbar(E, phi, yerr=[dlo, dup], ls='none', marker=marker, ms=11,
                    color=color, markeredgecolor=color, markerfacecolor='white',
                    markeredgewidth=2.0, elinewidth=2.0, capsize=4, zorder=zorder)

    def plot_points(self, ax, filename, color, zorder=1, marker='o'):
        """Differential measurements; bins with a null upper error are upper limits."""
        E, dElo, dEup, phi, dlo, dup = self.load(filename)[:6]

        limits = dup <= 0.0
        if np.any(~limits):
            m = ~limits
            ax.errorbar(E[m], phi[m], xerr=[dElo[m], dEup[m]], yerr=[dlo[m], dup[m]],
                        ls='none', marker=marker, ms=8, color=color,
                        markeredgecolor=color, elinewidth=2.0, capsize=0,
                        zorder=zorder)
        if np.any(limits):
            m = limits
            ax.errorbar(E[m], phi[m], xerr=[dElo[m], dEup[m]],
                        yerr=[dlo[m], np.zeros(m.sum())], ls='none',
                        marker='v', ms=8, color=color, markeredgecolor=color,
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
        self.plot_measured_lines(ax, 'Measured_integrals.txt', self.experiments['KamLAND'],
                                 self.SOLAR_LINE_DISPLAY_SCALE, zorder=16, marker='D')

        # Atmospheric spectra: Super-K measures nu_e (circles) and nu_mu
        # (squares); the IceCube unfolding (triangles) is nu_mu only.
        self.plot_points(ax, 'SuperK_atm_nue_points.txt',
                         self.experiments['Super-K'], zorder=16, marker='o')
        self.plot_points(ax, 'SuperK_atm_numu_points.txt',
                         self.experiments['Super-K'], zorder=16, marker='s')
        self.plot_points(ax, 'IceCube_atm_numu_points.txt',
                         self.experiments['IceCube'], zorder=16, marker='^')

        self.plot_points(ax, 'IceCube_combinedfit_points.txt',
                         self.experiments['IceCube'], zorder=17)
        self.plot_points(ax, 'IceCube_mese_points.txt',
                         self.experiments['IceCube'], zorder=17, marker='s')
        self.plot_points(ax, 'IceCube_glashow_points.txt',
                         self.experiments['IceCube'], zorder=17, marker='*')
        self.plot_points(ax, 'KM3NeT_km3_230213A_points.txt',
                         self.experiments['KM3NeT'], zorder=18, marker='D')

    # ------------------------------------------------------------ decoration

    # text, x [eV], y [flux], colour key, font size
    labels = [
        (r'C$\nu$B', 3.0e-4, 2.0e16, 'CNB', 20),
        (r'$n$', 4.0e-5, 3.0e6, 'BBN', 18),
        (r'$^3$H', 4.0e-3, 2.0e-6, 'BBN', 18),
        (r'Solar (thermal)', 5.0e0, 3.0e4, 'solar_thermal', 18),
        (r'$pp$', 7.0e4, 1.5e7, 'solar_nuclear', 18),
        (r'$^7$Be', 6.5e5, 2.0e5, 'solar_nuclear', 18),
        (r'$pep$', 3.2e6, 1.2e4, 'solar_nuclear', 18),
        (r'$^8$B', 3.0e7, 3.0e-1, 'solar_nuclear', 18),
        (r'hep', 4.5e7, 3.0e-4, 'solar_nuclear', 18),
        (r'DSNB', 1.1e8, 5.0e-6, 'DSNB', 18),
        (r'Atmospheric', 2.0e9, 5.0e-9, 'atmospheric', 18),
        (r'Astrophysical', 5.0e13, 3.0e-21, 'astrophysical', 18),
        (r'Cosmogenic', 2.5e17, 3.0e-29, 'cosmogenic', 18),
    ]

    # Components buried in the crowded 10 keV - 10 MeV region get a leader line:
    # text, x_text, y_text, x_tip, y_tip, colour key
    arrow_labels = [
        (r'CNO', 1.7e3, 3.0e0, 2.0e4, 1.6e0, 'solar_nuclear'),
        (r'Geoneutrinos', 5.0e4, 6.0e-7, 1.5e5, 2.0e1, 'geoneutrinos'),
        (r'Reactors', 1.3e7, 2.0e1, 4.0e6, 6.0e-1, 'reactor'),
    ]

    # Diagonal guide lines marking how many neutrinos above E cross unit area
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

    # All six labels are stacked on this vertical, in the empty left half.
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

    def annotate(self, ax):
        for text, x, y, key, size in self.labels:
            ax.text(x, y, text, color=self.colors[key], fontsize=size,
                    zorder=25, ha='center', va='center')

        for text, xt, yt, x, y, key in self.arrow_labels:
            ax.annotate(text, xy=(x, y), xytext=(xt, yt), color=self.colors[key],
                        fontsize=18, zorder=25, ha='center', va='center',
                        arrowprops=dict(arrowstyle='->', color=self.colors[key],
                                        lw=1.3, shrinkA=6, shrinkB=3))

        notes = [
            r'Model components: Vitagliano, Tamborra \& Raffelt, '
            r'Rev.\ Mod.\ Phys.\ 92 (2020) 045006 [arXiv:1910.11878]',
            r'Stems are monochromatic lines: height is an \emph{integral} flux in '
            r'cm$^{-2}$ s$^{-1}$, offset down by $10^{6}$ for the solar ones',
            r'Dotted diagonals: rate above $E$ through unit area, '
            r'$N(>E) = E\,\Phi(E)$ for an $E^{-2}$ spectrum',
        ]
        for i, note in enumerate(notes):
            ax.text(0.013, 0.078 - 0.024 * i, note, transform=ax.transAxes,
                    fontsize=13, color='tab:gray', zorder=25, va='bottom')

        ax.text(1.012, 0.5, CREDIT_URL, transform=ax.transAxes, rotation=-90,
                fontsize=12, color='tab:gray', ha='left', va='center', zorder=25)

    def experiment_legend(self, ax):
        """Colour key of the measurements, in the style of The_CR_Spectrum."""
        ax.text(0.985, 0.945, r'Measurements', transform=ax.transAxes,
                color='black', fontsize=17, ha='right', zorder=25)
        for i, (name, color) in enumerate(self.experiments.items()):
            entry = f'{name} ({self.experiment_years[name]})'
            ax.text(0.985, 0.945 - 0.035 * (i + 1), entry, transform=ax.transAxes,
                    color=color, fontsize=16, ha='right', zorder=25)
