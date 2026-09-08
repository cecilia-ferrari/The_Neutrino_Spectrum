"""Convert the GUNS ancillary tables of arXiv:1910.11878 into plot-ready files.

The original tables (``data/source/guns_tables``) are the ancillary material of

    E. Vitagliano, I. Tamborra, G. Raffelt,
    "Grand Unified Neutrino Spectrum at Earth",
    Rev. Mod. Phys. 92 (2020) 045006 [arXiv:1910.11878]

They come with heterogeneous column layouts and a few of them carry an explicit
power-of-ten prefactor in their header.  This script normalises everything to

    E [eV]   and   Phi [eV^-1 cm^-2 s^-1]

with the exception of the monochromatic components ("lines"), which stay as
integral fluxes in cm^-2 s^-1, exactly as in the original figure.

Output conventions (``data/output``):

    *_flux.txt   E, Phi
    *_band.txt   E, Phi_min, Phi_max
    *_lines.txt  E, Phi_integral [cm^-2 s^-1]
"""

from pathlib import Path

import numpy as np

from utils import read_table, write_columns

BASE_DIR = Path(__file__).resolve().parent
SOURCE_DIR = BASE_DIR / 'source' / 'guns_tables'
OUTPUT_DIR = BASE_DIR / 'output'

# Prefactors quoted in the headers of the original tables.
COSMOGENIC_SCALE = 1e-30
ICECUBE_SCALE = 1e-20

# Sun-lines.dat is *not* in the cm^-2 s^-1 its header claims.  The
# `Produce-your-GUNS` notebook shipped with the paper draws the solar lines at
#
#     10^-6 * 10^(Log10(flux) - 0.03)
#
# i.e. the tabulated numbers are the true integral fluxes divided by 10^6 and by
# a cosmetic 10^0.03 nudge that keeps the marker just below the true value.  We
# undo both, so that the file we write holds physical fluxes; the 10^-6 is
# re-applied at plotting time as an explicit, documented display scale.
# The check is unambiguous: the table gives 4018.22 for the 0.863 MeV 7Be
# branch, and 4018.22 * 10^6 * 10^0.03 = 4.31e9 cm^-2 s^-1 = 0.897 * 4.80e9,
# the Standard Solar Model value hard-coded in the notebook.
SUN_LINES_SCALE = 1e6 * 10 ** 0.03

# CNB-lines.dat, by contrast, is drawn unscaled by the same notebook and is
# therefore already in cm^-2 s^-1.

FLUX_HEADER = '# E [eV] - Phi [eV^-1 cm^-2 s^-1]\n'
BAND_HEADER = '# E [eV] - Phi_min [eV^-1 cm^-2 s^-1] - Phi_max [eV^-1 cm^-2 s^-1]\n'
LINE_HEADER = '# E [eV] - Phi [cm^-2 s^-1] (integral flux of a monochromatic line)\n'


def write_flux(name, E, phi):
    write_columns(OUTPUT_DIR / f'{name}_flux.txt', FLUX_HEADER, E, phi)


def write_band(name, E, lo, up):
    write_columns(OUTPUT_DIR / f'{name}_band.txt', BAND_HEADER,
                  E, np.minimum(lo, up), np.maximum(lo, up))


def write_lines(name, E, phi):
    write_columns(OUTPUT_DIR / f'{name}_lines.txt', LINE_HEADER, E, phi)


def convert_single_column(source, name, scale=1.0):
    """Tables shaped as (E, Phi)."""
    t = read_table(SOURCE_DIR / source)
    write_flux(name, t[:, 0], scale * t[:, 1])


def convert_band(source, name, col_lo=1, col_up=2, scale=1.0):
    """Tables shaped as (E, Phi_min, Phi_max)."""
    t = read_table(SOURCE_DIR / source)
    write_band(name, t[:, 0], scale * t[:, col_lo], scale * t[:, col_up])


def convert_cnb():
    convert_single_column('CNB.dat', 'CNB')
    t = read_table(SOURCE_DIR / 'CNB-lines.dat')
    write_lines('CNB', t[:, 0], t[:, 1])


def convert_sun():
    convert_single_column('Sun-thermal.dat', 'Sun_thermal')
    convert_single_column('Sun-nuclear-pp.dat', 'Sun_pp')
    convert_single_column('Sun-nuclear-B8.dat', 'Sun_B8')
    convert_band('Sun-nuclear-hep.dat', 'Sun_hep')
    convert_band('Sun-nuclear-N13.dat', 'Sun_N13')
    convert_band('Sun-nuclear-O15.dat', 'Sun_O15')

    t = read_table(SOURCE_DIR / 'Sun-lines.dat')
    write_lines('Sun', t[:, 0], SUN_LINES_SCALE * t[:, 1])

    # The CNO cycle is measured as a whole, so we also store the sum of the two
    # dominant beta decays on a common grid.  17F is neglected, as in the GUNS
    # tables themselves.
    n13 = read_table(SOURCE_DIR / 'Sun-nuclear-N13.dat')
    o15 = read_table(SOURCE_DIR / 'Sun-nuclear-O15.dat')
    E = np.unique(np.concatenate([n13[:, 0], o15[:, 0]]))
    cno = []
    for col in (1, 2):
        cno.append(np.interp(E, n13[:, 0], n13[:, col], left=0.0, right=0.0)
                   + np.interp(E, o15[:, 0], o15[:, col], left=0.0, right=0.0))
    write_band('Sun_CNO', E, cno[0], cno[1])


def convert_terrestrial():
    convert_single_column('Geoneutrinos.dat', 'Geoneutrinos')
    convert_single_column('Reactor.dat', 'Reactor')
    convert_single_column('BBN-tritium.dat', 'BBN_tritium')
    convert_single_column('BBN-neutron.dat', 'BBN_neutron')


def convert_atmospheric():
    t = read_table(SOURCE_DIR / 'Atmospheric.dat')
    write_flux('Atmospheric_nu', t[:, 0], t[:, 1])
    write_flux('Atmospheric_antinu', t[:, 0], t[:, 2])


def convert_dsnb():
    # Columns: E, nu(min), nu(max), antinu(min), antinu(max)
    t = read_table(SOURCE_DIR / 'DSNB.dat')
    write_band('DSNB_nu', t[:, 0], t[:, 1], t[:, 2])
    write_band('DSNB_antinu', t[:, 0], t[:, 3], t[:, 4])


def convert_cosmogenic():
    t = read_table(SOURCE_DIR / 'Cosmogenic.dat')
    write_flux('Cosmogenic_He', t[:, 0], COSMOGENIC_SCALE * t[:, 1])
    write_flux('Cosmogenic_Fe', t[:, 0], COSMOGENIC_SCALE * t[:, 2])


def convert_icecube_guns():
    convert_band('IceCube.dat', 'IceCube2017', scale=ICECUBE_SCALE)


def convert_all():
    convert_cnb()
    convert_sun()
    convert_terrestrial()
    convert_atmospheric()
    convert_dsnb()
    convert_cosmogenic()
    convert_icecube_guns()


if __name__ == '__main__':
    convert_all()
