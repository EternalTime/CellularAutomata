Two-Dimensional Automata
========================

In 1970 Martin Gardner devoted his Scientific American column to a game John
Conway had been playing on a Go board, and the mail that followed was — by
Gardner's own account — the largest response any column of his ever drew.
The Game of Life needs one sentence: a dead cell with exactly three live
neighbors is born, a live cell with two or three survives, and everything
else dies. From that sentence come gliders, oscillators, guns, and — as
Conway conjectured and others proved — universal computation.

B/S notation
^^^^^^^^^^^^

Life is one member of the outer-totalistic family: rules that update a cell
from its own value and the *sum* of its eight Moore neighbors, nothing more.
The family is named in B/S notation — B lists the neighbor counts at which a
dead cell is born, S the counts at which a live cell survives — making Life
B3/S23. The :class:`pyCA.ca2d.CA2D` class takes the two lists directly, and
Life gets a named constructor::

    from pyCA import CA2D

    life = CA2D.life((128, 128))      # random soup at density 0.5
    life.run(200)
    print(life.population)

    life.play()                       # watch it live; close to stop

The lattice is periodic in both directions, so gliders that leave one edge
arrive at the other.

Building from a known pattern
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Pass an explicit state to study a specific object. The glider, the smallest
spaceship, translates one cell diagonally every four steps — the repository's
test suite holds the implementation to exactly that::

    import numpy as np
    from pyCA import CA2D

    state = np.zeros((40, 40), dtype=int)
    for r, c in [(0, 1), (1, 2), (2, 0), (2, 1), (2, 2)]:
        state[r + 18, c + 18] = 1

    life = CA2D.life(state=state)
    life.run(4)        # the glider has moved by (1, 1)

Beyond Life
^^^^^^^^^^^

Change the two lists and the physics changes with them. HighLife (B36/S23)
adds a single birth condition to Life and gains a replicator. Seeds (B2/S)
is pure birth — nothing survives, yet the explosions are intricate. Day &
Night (B3678/S34678) is symmetric under exchanging live and dead cells, so
every pattern has a photographic negative with identical dynamics. ::

    highlife = CA2D([3, 6], [2, 3], shape=(128, 128))
    seeds    = CA2D([2], [], shape=(128, 128), fill=0.05)
    daynight = CA2D([3, 6, 7, 8], [3, 4, 6, 7, 8], shape=(128, 128))

Run a random soup under each and compare the late-time populations. Which
rules die, which saturate, and which hover? The measures in
:doc:`guide_measures` apply to 2d histories row by row — quantify what your
eyes report.
