"""Attach measured low-energy normalisations to the GUNS spectral shapes.

Borexino, SNO and KamLAND quote *integral* fluxes, which cannot be drawn on a
differential axis as such.  For the continuum components we therefore keep the
GUNS spectral shape and renormalise it so that its integral reproduces the
measured value, propagating the quoted uncertainty into a band:

    Phi_meas(E) = Phi_GUNS(E) * F_meas / integral(Phi_GUNS)

This is the usual "measured normalisation x Standard Solar Model shape"
construction; it is honest about what was measured (a rate) while remaining
comparable to the model curves.

The monochromatic lines (7Be, pep) are written out unchanged, in cm^-2 s^-1.
The same treatment is applied to measurements tagged 'integral', for which the
measured quantity and the GUNS curve do not span the same spectrum -- the
geoneutrino curve of the paper includes 40K, which is below the inverse-beta-decay
threshold and therefore invisible to KamLAND, so renormalising it to the
KamLAND U+Th flux would be meaningless.
"""

import csv
from pathlib import Path

import numpy as np

from utils import read_table, write_columns, write_data_to_file

BASE_DIR = Path(__file__).resolve().parent
SOURCE_FILE = BASE_DIR / 'source' / 'experiments' / 'IntegralFluxes.csv'
OUTPUT_DIR = BASE_DIR / 'output'

# Component name -> GUNS shape produced by convert_guns_tables.py
SHAPES = {
    'pp': 'Sun_pp_flux.txt',
    'B8': 'Sun_B8_flux.txt',
    'CNO': 'Sun_CNO_band.txt',
    'geo': 'Geoneutrinos_flux.txt',
}

BAND_HEADER = '# E [eV] - Phi_min [eV^-1 cm^-2 s^-1] - Phi_max [eV^-1 cm^-2 s^-1]\n'
LINE_HEADER = '# E [eV] - Phi [cm^-2 s^-1] - dPhi_lo - dPhi_up\n'

# kind -> output file collecting the integral-flux measurements
INTEGRAL_OUTPUT = {'line': 'Measured_lines.txt', 'integral': 'Measured_integrals.txt'}


def load_measurements():
    with SOURCE_FILE.open() as f:
        rows = [r for r in csv.reader(f) if r and not r[0].lstrip().startswith('#')]
    return [
        {
            'component': r[0].strip(),
            'experiment': r[1].strip(),
            'kind': r[2].strip(),
            'E_ref': float(r[3]),
            'flux': float(r[4]),
            'err_lo': float(r[5]),
            'err_up': float(r[6]),
        }
        for r in rows
    ]


def load_shape(component):
    """Return (E, Phi) for a GUNS component, averaging min/max if it is a band."""
    table = read_table(OUTPUT_DIR / SHAPES[component])
    E = table[:, 0]
    phi = table[:, 1] if table.shape[1] == 2 else 0.5 * (table[:, 1] + table[:, 2])
    return E, phi


def renormalise(component, flux, err_lo, err_up):
    E, phi = load_shape(component)
    norm = np.trapezoid(phi, E) if hasattr(np, 'trapezoid') else np.trapz(phi, E)
    if norm <= 0:
        raise RuntimeError(f'Cannot renormalise {component}: null model integral')
    shape = phi / norm
    return E, shape * (flux - err_lo), shape * (flux + err_up)


def convert_all():
    integrals = {kind: [] for kind in INTEGRAL_OUTPUT}

    for m in load_measurements():
        if m['kind'] == 'continuum':
            E, lo, up = renormalise(m['component'], m['flux'], m['err_lo'], m['err_up'])
            name = f"{m['experiment']}_{m['component']}_band.txt"
            write_columns(OUTPUT_DIR / name, BAND_HEADER, E, lo, up)
        else:
            integrals[m['kind']].append(
                f"{m['E_ref']:14.6e} {m['flux']:14.6e} "
                f"{m['err_lo']:14.6e} {m['err_up']:14.6e}\n")

    for kind, rows in integrals.items():
        if rows:
            write_data_to_file(OUTPUT_DIR / INTEGRAL_OUTPUT[kind], LINE_HEADER, rows)


if __name__ == '__main__':
    convert_all()
