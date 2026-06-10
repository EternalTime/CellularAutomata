# CellularAutomata

pyCA is a Python library for building cellular automata and measuring the
information their histories carry. It covers the elementary CAs (Wolfram
rules 0–255), an Ising variant where a deterministic rule competes with a
heat bath, noisy and asynchronous rule corruptions, and outer-totalistic 2d
automata — Conway's Game of Life included — together with block entropy,
entropy rate, and mutual information for the resulting spacetime diagrams.

The original MATLAB classes (2016) live on in `matlab/`.

## Installation

```bash
git clone https://github.com/EternalTime/CellularAutomata.git
cd CellularAutomata
pip install -e .
```

Requires Python 3.8+; numpy and matplotlib are installed automatically.

## Quick start

```python
from pyCA import ECA, CA2D, measures

# rule 110 on a random lattice of 256 cells
ca = ECA(110, N=256)
ca.run(500)
print(measures.entropy_rate(ca.spacetime(), k=4))

# watch it live (close the window to stop)
ca.play()

# Conway's Game of Life
life = CA2D.life((128, 128))
life.run(200)
print(life.population)
```

The Ising and stochastic families follow the same pattern:

```python
from pyCA import ICA, NoisyECA, AsyncECA

ica = ICA(110, temperature=1.5, stochfrac=0.3, N=256)
noisy = NoisyECA(90, noise=0.01, N=256)
lazy = AsyncECA(30, update_fraction=0.7, N=256)
```

## Documentation

Sphinx documentation lives in `docs/`; build with `make -C docs html`. The
guides walk through each family and the information measures.

## Tests

```bash
pip install pytest
pytest
```

## License

MIT
