"""Convert the Super-Kamiokande DSNB flux limits into the units of the figure.

Source: Table 6 of arXiv:2511.02222 (ApJ accepted), the 956.2-day
gadolinium-loaded Super-Kamiokande dataset.

The published limits are differential, in cm^-2 s^-1 MeV^-1, and are on the
electron antineutrino flux.  That is already a single species and already
integrated over the sky, which is exactly the convention of the GUNS curves, so
the only conversion needed is MeV^-1 -> eV^-1:

    Phi [eV^-1 cm^-2 s^-1] = limit [cm^-2 s^-1 MeV^-1] * 1e-6

They are written in the usual points format with a null upper error, the
convention this repository uses to mark an upper limit.
"""

import csv
from pathlib import Path

import numpy as np

from utils import write_data_to_file

BASE_DIR = Path(__file__).resolve().parent
SOURCE_FILE = BASE_DIR / 'source' / 'experiments' / 'SuperK2026_DSNB_limits.csv'
OUTPUT_FILE = BASE_DIR / 'output' / 'SuperK_DSNB_limits_points.txt'

MEV_TO_EV = 1e6
PER_MEV_TO_PER_EV = 1e-6

# How far below the limit the downward arrow is drawn, as a fraction of it.
ARROW_FRACTION = 0.5

HEADER = ('# Super-Kamiokande 90% C.L. upper limits on the DSNB nu_e-bar flux\n'
          '# E [eV] - dE_lo - dE_up - Phi [eV^-1 cm^-2 s^-1] - dPhi_lo - dPhi_up\n'
          '# dPhi_up = 0 marks an upper limit\n')


def convert():
    with SOURCE_FILE.open() as f:
        rows = [r for r in csv.reader(f) if r and not r[0].lstrip().startswith('#')]

    E_lo = np.array([float(r[0]) for r in rows]) * MEV_TO_EV
    E_up = np.array([float(r[1]) for r in rows]) * MEV_TO_EV
    phi = np.array([float(r[2]) for r in rows]) * PER_MEV_TO_PER_EV

    # Geometric centre of each bin, as elsewhere in this repository.
    E = np.sqrt(E_lo * E_up)

    columns = (E, E - E_lo, E_up - E, phi,
               ARROW_FRACTION * phi, np.zeros_like(phi))
    lines = [' '.join(f'{v:14.6e}' for v in row) + '\n' for row in zip(*columns)]
    write_data_to_file(OUTPUT_FILE, HEADER, lines)


if __name__ == '__main__':
    convert()
