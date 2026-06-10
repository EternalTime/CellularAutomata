"""pyCA: cellular automata and their information content.

A small library for building cellular automata — deterministic, thermal,
noisy, asynchronous, one- and two-dimensional — and measuring the
information their histories carry.

Modules
-------
eca
    Elementary cellular automata (Wolfram rules 0-255).
ica
    Ising cellular automata: ECA rules competing with a heat bath.
stochastic
    Noisy and asynchronous variants of the elementary CAs.
ca2d
    Outer-totalistic 2d automata, Conway's Game of Life included.
measures
    Block entropy, entropy rate, and mutual information for CA histories.
"""
def docs():
    """Open the online pyCA documentation in a web browser."""
    import webbrowser
    webbrowser.open('https://damiansowinski.com/pyCA/')

from pyCA.eca import ECA
from pyCA.ica import ICA
from pyCA.stochastic import NoisyECA, AsyncECA
from pyCA.ca2d import CA2D
from pyCA import measures

__all__ = ['ECA', 'ICA', 'NoisyECA', 'AsyncECA', 'CA2D', 'measures', 'docs']
