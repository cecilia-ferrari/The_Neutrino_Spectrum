"""Convert the measured atmospheric neutrino spectra into GUNS units.

Super-Kamiokande and IceCube both publish

    E^2 Phi   in   GeV cm^-2 s^-1 sr^-1,

per flavour and summed over neutrinos and antineutrinos, since neither detector
separates the two.  The GUNS figure shows a single species -- one flavour, nu and
nubar drawn as separate curves -- so, exactly as in
``convert_neutrino_telescopes.py``, we multiply by 4*pi and divide by 2:

    Phi = (E^2 Phi) * 4*pi / 2 / E^2,     GeV^-1 -> eV^-1.

A caveat worth keeping in mind when reading the result: the GUNS atmospheric
curve is a *production* flux, whereas these are fluxes measured at a detector.
Below ~10 GeV the Super-K nu_mu points therefore sit under the curve because of
nu_mu -> nu_tau oscillations, which the model does not include.  Above ~100 GeV
oscillations are irrelevant and the residual offset is the genuine difference
between the Honda-based model and the unfolded measurements.
"""

import csv
import math
from pathlib import Path

import numpy as np

from utils import write_data_to_file

BASE_DIR = Path(__file__).resolve().parent
SOURCE_DIR = BASE_DIR / 'source' / 'experiments'
OUTPUT_DIR = BASE_DIR / 'output'

GEV_TO_EV = 1e9
SOLID_ANGLE = 4.0 * math.pi
SPECIES_FACTOR = 0.5       # published nu + nubar -> single species

DATASETS = [
    ('SuperK2016_atmospheric.csv', 'SuperK_atm'),
    ('IceCube2011_atmospheric_numu.csv', 'IceCube_atm'),
]

HEADER = '# E [eV] - dE_lo - dE_up - Phi [eV^-1 cm^-2 s^-1] - dPhi_lo - dPhi_up\n'


def read_rows(filename):
    with Path(filename).open() as f:
        rows = [r for r in csv.reader(f) if r and not r[0].lstrip().startswith('#')]
    out = []
    for flavour, lo, hi, ref, e2phi, elo, eup in rows:
        lo, hi, ref = float(lo), float(hi), float(ref)
        if math.isnan(ref):
            ref = 0.5 * (lo + hi)       # geometric centre of the bin
        out.append({
            'flavour': flavour.strip(),
            'E_lo': 10.0 ** lo, 'E_up': 10.0 ** hi, 'E': 10.0 ** ref,
            'e2phi': float(e2phi),
            'err_lo': float(elo) / 100.0, 'err_up': float(eup) / 100.0,
        })
    return out


def to_guns_units(E_gev, e2phi):
    """(E^2 Phi) [GeV cm^-2 s^-1 sr^-1] -> Phi [eV^-1 cm^-2 s^-1], one species."""
    return e2phi * SOLID_ANGLE * SPECIES_FACTOR / (E_gev ** 2 * GEV_TO_EV)


def convert(rows):
    E = np.array([r['E'] for r in rows])
    phi = np.array([to_guns_units(r['E'], r['e2phi']) for r in rows])
    dElo = E - np.array([r['E_lo'] for r in rows])
    dEup = np.array([r['E_up'] for r in rows]) - E
    dlo = phi * np.array([r['err_lo'] for r in rows])
    dup = phi * np.array([r['err_up'] for r in rows])
    return (E * GEV_TO_EV, dElo * GEV_TO_EV, dEup * GEV_TO_EV, phi, dlo, dup)


def convert_all():
    for source, prefix in DATASETS:
        rows = read_rows(SOURCE_DIR / source)
        for flavour in sorted({r['flavour'] for r in rows}):
            selected = [r for r in rows if r['flavour'] == flavour]
            columns = convert(selected)
            lines = [' '.join(f'{v:14.6e}' for v in row) + '\n'
                     for row in zip(*columns)]
            write_data_to_file(OUTPUT_DIR / f'{prefix}_{flavour}_points.txt',
                               HEADER, lines)


if __name__ == '__main__':
    convert_all()
