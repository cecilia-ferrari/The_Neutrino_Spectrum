"""Convert high-energy neutrino-telescope data releases into GUNS units.

The public IceCube / KM3NeT tables are quoted as a *per-flavour*, *per-steradian*
quantity

    E^2 Phi   in   1e-8 GeV cm^-2 s^-1 sr^-1

where "per flavour" means nu_l + nubar_l summed.  The GUNS figure instead shows
the angle-integrated flux of a *single* species (one flavour, neutrinos and
antineutrinos separately),

    Phi   in   eV^-1 cm^-2 s^-1

so the conversion is

    Phi = (E^2 Phi) * 4*pi / 2 / E^2

with E in GeV, followed by GeV^-1 -> eV^-1.  The factor 1/2 splits the published
nu + nubar flux into the two species; no flavour factor is applied because the
GUNS convention is already per flavour.

Output: E [eV], dE_lo, dE_up, Phi, dPhi_lo, dPhi_up  (upper limits are flagged
by dPhi_up == 0, following the convention of The_CR_Spectrum).
"""

import math
from pathlib import Path

import numpy as np

from utils import write_data_to_file

BASE_DIR = Path(__file__).resolve().parent
SOURCE_DIR = BASE_DIR / 'source' / 'experiments'
OUTPUT_DIR = BASE_DIR / 'output'

CSV_UNIT = 1e-8            # tables are in 1e-8 GeV cm^-2 s^-1 sr^-1
GEV_TO_EV = 1e9
SOLID_ANGLE = 4.0 * math.pi
SPECIES_FACTOR = 0.5       # published nu + nubar -> single species

DATASETS = [
    ('IceCube2026_combinedfit.csv', 'IceCube_combinedfit', 'central'),
    ('IceCube2026_mese.csv', 'IceCube_mese', 'central'),
    ('IceCube2021_Glashow.csv', 'IceCube_glashow', 'edges'),
    ('KM3NeT2025_km3_230213A.csv', 'KM3NeT_km3_230213A', 'central'),
]

HEADER = '# E [eV] - dE_lo - dE_up - Phi [eV^-1 cm^-2 s^-1] - dPhi_lo - dPhi_up\n'


def _to_guns_units(E_gev, e2phi):
    """(E^2 Phi) [1e-8 GeV cm^-2 s^-1 sr^-1] -> Phi [eV^-1 cm^-2 s^-1]."""
    return e2phi * CSV_UNIT * SOLID_ANGLE * SPECIES_FACTOR / (E_gev ** 2 * GEV_TO_EV)


def convert(filename, layout):
    cols = np.loadtxt(filename, delimiter=',', comments='#', unpack=True, ndmin=2)

    if layout == 'central':
        x, xmin, xmax, y, y_lo, y_up = cols[:6]
    else:  # 'edges': the Glashow release only quotes the bin edges
        xmin, xmax, y, y_lo, y_up = cols[:5]
        x = np.sqrt(xmin * xmax)

    dxLo = np.abs(x - xmin) * GEV_TO_EV
    dxUp = np.abs(x - xmax) * GEV_TO_EV

    # A vanishing lower edge marks a bin for which only an upper limit is given.
    measured = y_lo > 0

    central = np.where(measured, y, y_up)
    phi = _to_guns_units(x, central)
    dphi_lo = _to_guns_units(x, np.where(measured, central - y_lo, 0.5 * central))
    dphi_up = _to_guns_units(x, np.where(measured, y_up - central, 0.0))

    return x * GEV_TO_EV, dxLo, dxUp, phi, dphi_lo, dphi_up


def convert_all():
    for source, name, layout in DATASETS:
        columns = convert(SOURCE_DIR / source, layout)
        lines = [' '.join(f'{v:14.6e}' for v in row) + '\n' for row in zip(*columns)]
        write_data_to_file(OUTPUT_DIR / f'{name}_points.txt', HEADER, lines)


if __name__ == '__main__':
    convert_all()
