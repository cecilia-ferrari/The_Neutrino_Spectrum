import numpy as np
import pytest

from PlotFuncs import TheNuSpectrum


def test_tables_are_loadable_and_positive():
    """Every plot-ready table must be finite and non-negative."""
    plot = TheNuSpectrum()
    files = sorted(plot.datadir.glob('*.txt'))
    assert files, 'no converted tables found: run the scripts in data/ first'
    for f in files:
        table = np.loadtxt(f, comments='#', ndmin=2)
        assert np.all(np.isfinite(table)), f'non-finite entry in {f.name}'
        assert np.all(table[:, 0] > 0.0), f'non-positive energy in {f.name}'


def test_solar_line_normalisation():
    """The 7Be and pep lines must come back as physical integral fluxes."""
    plot = TheNuSpectrum()
    E, phi = plot.load('Sun_lines.txt')[:2]
    be7 = phi[np.argmin(np.abs(E - 8.63e5))]
    pep = phi[np.argmin(np.abs(E - 1.445e6))]
    # Standard Solar Model values hard-coded in the paper's own notebook.
    assert be7 == pytest.approx(0.897 * 4.80e9, rel=1e-3)
    assert pep == pytest.approx(1.448e8, rel=1e-3)


@pytest.mark.mpl_image_compare(tolerance=0.5, savefig_kwargs={'dpi': 200})
def test_guns_plot():
    plot = TheNuSpectrum()
    fig, ax = plot.FigSetup()
    plot.model(ax)
    plot.data(ax)
    plot.annotate(ax)
    plot.experiment_legend(ax)
    return fig
