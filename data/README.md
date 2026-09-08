## Data

`source/` holds untouched inputs, `output/` the plot-ready tables produced by the
conversion scripts in this directory. Nothing in `output/` is edited by hand;
delete it and re-run the three scripts to rebuild it.

### `source/guns_tables/`

The 17 ancillary data tables of
[arXiv:1910.11878](https://arxiv.org/abs/1910.11878), downloaded from
`https://arxiv.org/src/1910.11878/anc/tables/`. Credit: E. Vitagliano,
I. Tamborra and G. Raffelt, Rev. Mod. Phys. 92 (2020) 045006.

Two of them carry a prefactor in their header, which `convert_guns_tables.py`
undoes: `Cosmogenic.dat` is in 10⁻³⁰ eV⁻¹ cm⁻² s⁻¹ and `IceCube.dat` in
10⁻²⁰ eV⁻¹ cm⁻² s⁻¹.

A third, `Sun-lines.dat`, is mislabelled: its header claims cm⁻² s⁻¹ but the
values are the true integral fluxes divided by 10⁶ and by a cosmetic 10⁰·⁰³. This
is verifiable against the paper's own `Produce-your-GUNS.nb` notebook, which
draws the 0.863 MeV ⁷Be line at `10⁻⁶ × 10^(Log10(0.897 × 4.80×10⁹) − 0.03)`;
`4018.22 × 10⁶ × 10⁰·⁰³ = 4.31×10⁹ cm⁻² s⁻¹`, exactly the tabulated value. The
converter restores the physical flux. `CNB-lines.dat`, drawn unscaled by the same
notebook, is left alone.

### `source/experiments/`

| File | Content | Origin |
|---|---|---|
| `IceCube2026_combinedfit.csv` | diffuse astrophysical flux, combined fit | [Harvard Dataverse](https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/ZBO52I) |
| `IceCube2026_mese.csv` | diffuse astrophysical flux, MESE sample | as above |
| `IceCube2021_Glashow.csv` | Glashow resonance candidate | [IceCube data release](https://icecube.wisc.edu/data-releases/2021/03/icecube-data-for-the-first-glashow-resonance-candidate/) |
| `KM3NeT2025_km3_230213A.csv` | KM3-230213A event | KM3NeT, Nature 638 (2025) 376 |
| `IntegralFluxes.csv` | Borexino / SNO / KamLAND integral fluxes | hand-compiled, references in the file header |

The four CSVs are taken as curated by
[`The_CR_Spectrum`](https://github.com/carmeloevoli/The_CR_Spectrum/tree/master/data/source).

### `output/` file conventions

| Suffix | Columns | Units |
|---|---|---|
| `*_flux.txt` | `E`, `Phi` | eV, eV⁻¹ cm⁻² s⁻¹ |
| `*_band.txt` | `E`, `Phi_min`, `Phi_max` | eV, eV⁻¹ cm⁻² s⁻¹ |
| `*_lines.txt` | `E`, `Phi` | eV, cm⁻² s⁻¹ (integral) |
| `Measured_*.txt` | `E`, `Phi`, `dPhi_lo`, `dPhi_up` | eV, cm⁻² s⁻¹ (integral) |
| `*_points.txt` | `E`, `dE_lo`, `dE_up`, `Phi`, `dPhi_lo`, `dPhi_up` | eV, eV⁻¹ cm⁻² s⁻¹ |

In `*_points.txt` a row with `dPhi_up == 0` is an upper limit.
