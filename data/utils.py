"""Small helpers shared by the conversion scripts."""

import logging
from pathlib import Path

import numpy as np


def read_table(filename):
    """Read one of the GUNS ancillary tables.

    The tables carry a free-form textual header of variable length, so instead
    of skipping a fixed number of rows we simply keep every line that parses
    entirely as floats.
    """
    rows = []
    with Path(filename).open() as f:
        for line in f:
            fields = line.split()
            if not fields:
                continue
            try:
                rows.append([float(x) for x in fields])
            except ValueError:
                continue

    if not rows:
        raise RuntimeError(f'No numerical rows found in {filename}')

    ncols = max(len(r) for r in rows)
    rows = [r for r in rows if len(r) == ncols]

    table = np.array(rows)
    return table[np.argsort(table[:, 0])]


def write_data_to_file(filename, header, data):
    """Write a header and an iterable of data lines to a text file."""
    path = Path(filename)
    path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with path.open('w') as f:
            f.write(header)
            for line in data:
                f.write(line)
        logging.info('Data successfully written to %s', path)
    except IOError as e:
        logging.error('Failed to write to file %s: %s', path, e)
        raise RuntimeError(f'Failed to write to file {path}') from e


def write_columns(filename, header, *columns):
    """Write an arbitrary number of equal-length columns in scientific notation."""
    lines = [' '.join(f'{v:14.6e}' for v in row) + '\n' for row in zip(*columns)]
    write_data_to_file(filename, header, lines)
