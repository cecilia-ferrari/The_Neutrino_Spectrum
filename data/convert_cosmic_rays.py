"""Convert the KISS cosmic-ray tables into the units of the GUNS figure.

Source tables come from the KISS Cosmic Ray DataBase
(github.com/carmeloevoli/KISS-CosmicRayDataBase), the same collection that feeds
carmeloevoli/The_CR_Spectrum, and are themselves built mostly on CRDB and KCDC.

x is either a rigidity [GV], a kinetic energy [GeV], a kinetic energy per nucleon
[GeV/n] or a total energy [GeV], and dJ/dx is in GeV^-1 m^-2 s^-1 sr^-1.

All files are taken from the repository's ``kiss_tables/`` directory, whose
copies are normalised to a single layout

    kiss6   x, dJ/dx, stat_lo, stat_up, sys_lo, sys_up

This matters: the same repository also ships the *raw* tables under
``data/KCDC/`` and ``data/mytables/``, and those use other column layouts and
separators.  The raw DAMPE proton table, for instance, starts with the two bin
edges, so reading it as ``kiss6`` silently returns the upper bin edge as the
flux and yields a spectrum that rises with energy.  ``check_falling_spectrum``
below exists to catch exactly that class of mistake.
The x -> total-energy conversion (and its Jacobian) is the one used by
The_CR_Spectrum, reproduced here so the two plots agree.

We then convert to the angle-integrated, per-eV, per-cm^2 units of the GUNS
figure:

    Phi [eV^-1 cm^-2 s^-1] = dJ/dE [GeV^-1 m^-2 s^-1 sr^-1] * 4*pi * 1e-4 * 1e-9

No species factor is applied: unlike the neutrino curves, which show a single
species, a cosmic-ray spectrum is simply a particle flux.

Statistical and systematic errors are added in quadrature, as in The_CR_Spectrum.
"""

import math
from pathlib import Path

import numpy as np

from utils import write_data_to_file

BASE_DIR = Path(__file__).resolve().parent
SOURCE_DIR = BASE_DIR / 'source' / 'cosmic_rays'
OUTPUT_DIR = BASE_DIR / 'output'

PROTON_MASS = 0.9382720813      # GeV
ELECTRON_MASS = 0.00051099895   # GeV

SPECIES = {
    'H': {'A': 1, 'Z': 1, 'mass': PROTON_MASS},
    'e+e-': {'A': 1, 'Z': 1, 'mass': ELECTRON_MASS},
    'allParticle': {'A': 1, 'Z': 1, 'mass': PROTON_MASS},
}

# GeV^-1 m^-2 s^-1 sr^-1  ->  eV^-1 cm^-2 s^-1, integrated over the sky
FLUX_SCALE = 4.0 * math.pi * 1e-4 * 1e-9
GEV_TO_EV = 1e9

# filename, experiment, species, x_kind, layout
GROUPS = {
    'allparticle': [
        ('HAWC_allParticle_totalEnergy.txt', 'HAWC', 'allParticle', 'energy', 'kiss6'),
        ('NUCLEON_allParticle_totalEnergy.txt', 'NUCLEON', 'allParticle', 'energy', 'kiss6'),
        ('KASCADE_2005_SIBYLL-2.1_allParticle_totalEnergy.txt', 'KASCADE', 'allParticle', 'energy', 'kiss6'),
        ('KASCADE-Grande_QGSJet-II-04_allParticle_totalEnergy.txt', 'KASCADE-Grande', 'allParticle', 'energy', 'kiss6'),
        ('IceTop_IceCube_SIBYLL-2.1_allParticle_totalEnergy.txt', 'IceTop+IceCube', 'allParticle', 'energy', 'kiss6'),
        ('Auger_hybrid_allParticle_totalEnergy.txt', 'Auger', 'allParticle', 'energy', 'kiss6'),
        ('Tibet_SIBYLL+HD_allParticle_totalEnergy.txt', 'Tibet', 'allParticle', 'energy', 'kiss6'),
        ('TUNKA-133_allParticle_totalEnergy.txt', 'TUNKA-133', 'allParticle', 'energy', 'kiss6'),
        ('TALE_allParticle_totalEnergy.txt', 'TALE', 'allParticle', 'energy', 'kiss6'),
        ('TA_allParticle_totalEnergy.txt', 'TA', 'allParticle', 'energy', 'kiss6'),
    ],
    'protons': [
        ('AMS-02_H_rigidity.txt', 'AMS-02', 'H', 'rigidity', 'kiss6'),
        ('BESS-TeV_H_kineticEnergy.txt', 'BESS-TeV', 'H', 'energy', 'kiss6'),
        ('CREAM_H_kineticEnergy.txt', 'CREAM', 'H', 'energy', 'kiss6'),
        ('CALET_H_kineticEnergy.txt', 'CALET', 'H', 'energy', 'kiss6'),
        ('DAMPE_H_kineticEnergy.txt', 'DAMPE', 'H', 'energy', 'kiss6'),
        ('LHAASO_SIBYLL-2.3d_H_totalEnergy.txt', 'LHAASO', 'H', 'energy', 'kiss6'),
        ('IceTop_IceCube_SIBYLL-2.1_H_totalEnergy.txt', 'IceTop+IceCube', 'H', 'energy', 'kiss6'),
        ('PAMELA_H_rigidity.txt', 'PAMELA', 'H', 'rigidity', 'kiss6'),
    ],
    'leptons': [
        ('AMS-02_e+e-_rigidity.txt', 'AMS-02', 'e+e-', 'rigidity', 'kiss6'),
        ('CALET_e+e-_totalEnergy.txt', 'CALET', 'e+e-', 'energy', 'kiss6'),
        ('DAMPE_e+e-_totalEnergy.txt', 'DAMPE', 'e+e-', 'energy', 'kiss6'),
        ('FERMI_e+e-_totalEnergy.txt', 'FERMI', 'e+e-', 'energy', 'kiss6'),
        ('VERITAS_e+e-_totalEnergy.txt', 'VERITAS', 'e+e-', 'energy', 'kiss6'),
    ],
}

# layout -> (x column, flux column, stat columns, sys columns or None)
LAYOUTS = {
    'kiss6': (0, 1, (2, 3), (4, 5)),
    'kcdc4': (0, 1, (2, 3), None),
    'kcdc6': (0, 1, (2, 3), (4, 5)),
    'calet8': (2, 3, (4, 5), (6, 7)),
}

HEADER_FMT = ('# Cosmic-ray {group} spectrum, converted from the KISS tables\n'
              '# Contributing measurements: {experiments}\n'
              '# E [eV] - dE_lo - dE_up - Phi [eV^-1 cm^-2 s^-1] - dPhi_lo - dPhi_up\n')


def read_columns(filename, layout):
    """Read a table that may be whitespace- or ';'-separated."""
    rows = []
    with Path(filename).open() as f:
        for line in f:
            line = line.split('#')[0].replace(';', ' ')
            fields = line.split()
            if not fields:
                continue
            try:
                rows.append([float(v) for v in fields])
            except ValueError:
                continue

    x_col, y_col, stat_cols, sys_cols = LAYOUTS[layout]
    needed = max([x_col, y_col, *stat_cols, *(sys_cols or ())]) + 1
    rows = [r for r in rows if len(r) == needed]
    if not rows:
        raise RuntimeError(f'{filename}: no rows with {needed} columns '
                           f'(layout {layout!r})')

    table = np.array(rows)
    stat_lo, stat_up = table[:, stat_cols[0]], table[:, stat_cols[1]]
    if sys_cols is None:
        sys_lo = sys_up = np.zeros(len(table))
    else:
        sys_lo, sys_up = table[:, sys_cols[0]], table[:, sys_cols[1]]
    return table[:, x_col], table[:, y_col], stat_lo, stat_up, sys_lo, sys_up


def load_spectrum(filename, species, x_kind, layout):
    """Load a KISS table and return the total energy [GeV] and dJ/dE."""
    x, dJdx, stat_lo, stat_up, sys_lo, sys_up = read_columns(filename, layout)
    info = SPECIES[species]

    if x_kind == 'rigidity':
        mass, charge = info['mass'], info['Z']
        energy = np.sqrt((charge * x) ** 2 + mass ** 2) - mass
        jacobian = (energy + mass) / (charge ** 2 * x)
    elif x_kind == 'energy_per_nucleon':
        energy = info['A'] * x
        jacobian = 1.0 / info['A']
    elif x_kind == 'energy':
        energy, jacobian = x, 1.0
    else:
        raise ValueError(f"Unknown x_kind '{x_kind}' for {filename}")

    flux = dJdx * jacobian
    err_lo = np.sqrt(stat_lo ** 2 + sys_lo ** 2) * jacobian
    err_up = np.sqrt(stat_up ** 2 + sys_up ** 2) * jacobian
    return energy, flux, err_lo, err_up


def check_falling_spectrum(name, E, phi):
    """Guard against a column mix-up.

    Every cosmic-ray spectrum here falls steeply with energy, by many decades
    across the measured range.  Comparing the first and last decile of the
    points is a blunt but effective test: a table read with the wrong columns
    (see the module docstring) fails it immediately.
    """
    order = np.argsort(E)
    phi = phi[order]
    n = max(1, len(phi) // 10)
    if np.median(phi[-n:]) >= np.median(phi[:n]):
        raise RuntimeError(
            f'{name}: flux does not fall with energy '
            f'({np.median(phi[:n]):.3e} -> {np.median(phi[-n:]):.3e}); '
            'the table was almost certainly read with the wrong columns')


def convert_group(group, datasets):
    E, phi, dlo, dup = [], [], [], []
    for filename, _experiment, species, x_kind, layout in datasets:
        e, f, lo, up = load_spectrum(SOURCE_DIR / filename, species, x_kind, layout)
        check_falling_spectrum(filename, e, f)
        E.append(e * GEV_TO_EV)
        phi.append(f * FLUX_SCALE)
        dlo.append(lo * FLUX_SCALE)
        dup.append(up * FLUX_SCALE)

    E = np.concatenate(E)
    phi, dlo, dup = (np.concatenate(a) for a in (phi, dlo, dup))

    order = np.argsort(E)
    E, phi, dlo, dup = E[order], phi[order], dlo[order], dup[order]

    # A lower error reaching down to zero flux marks an upper limit, following
    # the same convention as the neutrino point files.
    dup = np.where(dlo >= phi, 0.0, dup)

    zeros = np.zeros_like(E)
    header = HEADER_FMT.format(
        group=group, experiments=', '.join(d[1] for d in datasets))
    lines = [' '.join(f'{v:14.6e}' for v in row) + '\n'
             for row in zip(E, zeros, zeros, phi, dlo, dup)]
    write_data_to_file(OUTPUT_DIR / f'CR_{group}_points.txt', header, lines)


def convert_all():
    for group, datasets in GROUPS.items():
        convert_group(group, datasets)


if __name__ == '__main__':
    convert_all()
