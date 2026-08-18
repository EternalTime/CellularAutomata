Getting Started
===============

In this guide you will install pyCA and watch your first cellular automaton
compute.

Installation
^^^^^^^^^^^^

pyCA requires Python 3.8 or newer, numpy, and matplotlib. Clone the
repository and install it into a virtual environment::

    git clone https://github.com/EternalTime/CellularAutomata.git
    cd CellularAutomata
    python3 -m venv .venv
    source .venv/bin/activate
    python -m pip install --upgrade pip
    pip install -e .

The ``-e`` flag installs in editable mode, so changes to the source are
picked up immediately. Check the install::

    >>> import pyCA

First automaton
^^^^^^^^^^^^^^^

Rule 30 from a single live cell, the canonical demonstration that a trivial
rule need not behave trivially::

    import numpy as np
    import matplotlib.pyplot as plt
    from pyCA import ECA

    state = np.zeros(301, dtype=int)
    state[150] = 1

    ca = ECA(30, state)
    ca.run(150)

    plt.imshow(ca.spacetime(), cmap='binary', interpolation='nearest')
    plt.axis('off')
    plt.show()

The left edge of the triangle is periodic, the right edge is intricate, and
the center column is random enough that it once served as a random number
generator. Call ``ca.play()`` to watch an automaton evolve live instead;
close the window to stop.

Now ask the question the rest of this library is built to answer: *how much
information is in that picture?* ::

    from pyCA import measures

    print(measures.block_entropy(ca.spacetime(), k=3))
    print(measures.entropy_rate(ca.spacetime(), k=3))

Hold those numbers in hand as you read :doc:`guide_measures`.
