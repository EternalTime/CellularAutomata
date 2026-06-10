"""Two-dimensional outer-totalistic cellular automata.

An outer-totalistic rule updates each cell from its own value and the *sum*
of its eight (Moore) neighbors, nothing more. The family is conventionally
named in B/S notation: B lists the neighbor counts at which a dead cell is
born, S the counts at which a live cell survives. Conway's Game of Life is
B3/S23 — born with exactly three neighbors, surviving with two or three —
and remains the canonical inhabitant of the family.
"""

import numpy as np

class CA2D:
    """An outer-totalistic cellular automaton on a periodic 2d lattice.

    Parameters
    ----------
    births : sequence of int
        Neighbor counts (0-8) at which a dead cell becomes alive.
    survivals : sequence of int
        Neighbor counts (0-8) at which a live cell stays alive.
    state : array_like of 0s and 1s, optional
        Initial 2d state. If omitted, a random state of the given `shape`
        is drawn with density `fill`.
    shape : tuple of int, optional
        Lattice shape used when `state` is omitted (default (128, 128)).
    fill : float, optional
        Live-cell density of the random initial state (default 0.5).
    memory : int, optional
        Number of past states retained (default 256).
    rng : numpy.random.Generator, optional
        Random source; defaults to ``numpy.random.default_rng()``.

    Examples
    --------
    >>> from pyCA import CA2D
    >>> life = CA2D.life((64, 64))
    >>> life.run(100)
    >>> life.population
    ...
    """

    def __init__(self, births, survivals, state=None, shape=(128, 128),
                 fill=0.5, memory=256, rng=None):
        self._rng = rng if rng is not None else np.random.default_rng()
        if state is None:
            state = (self._rng.random(shape) < fill).astype(np.uint8)
        state = np.asarray(state)
        self.shape = state.shape
        self.memory = memory
        self._history = []
        self.births = births
        self.survivals = survivals
        self.state = state

    @classmethod
    def life(cls, shape=(128, 128), state=None, **kwargs):
        """Conway's Game of Life, B3/S23."""
        return cls([3], [2, 3], state=state, shape=shape, **kwargs)

    #------------------------------------------------ validated properties
    @property
    def births(self):
        return self._births

    @births.setter
    def births(self, counts):
        self._births = self._count_mask(counts)

    @property
    def survivals(self):
        return self._survivals

    @survivals.setter
    def survivals(self, counts):
        self._survivals = self._count_mask(counts)

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, newState):
        newState = np.asarray(newState)
        if newState.ndim != 2 or not np.isin(newState, [0, 1]).all():
            raise ValueError('state must be a 2d array of 0s and 1s')
        if hasattr(self, '_state') and newState.shape != self.shape:
            raise ValueError('state must keep its shape %s' % (self.shape,))
        self._state = newState.astype(np.uint8)
        self._remember(self._state)

    @property
    def population(self):
        """Number of live cells in the current state."""
        return int(self._state.sum())

    #------------------------------------------------------------ dynamics
    def evolve(self):
        """Advance the automaton one time step."""
        counts = self._neighbor_counts(self._state)
        alive = self._state.astype(bool)
        born = ~alive & self._births[counts]
        survive = alive & self._survivals[counts]
        self.state = (born | survive).astype(np.uint8)

    def run(self, steps):
        """Advance the automaton `steps` time steps."""
        for _ in range(steps):
            self.evolve()

    def history(self):
        """The remembered history as a (time, rows, columns) array."""
        return np.array(self._history)

    def play(self, interval=30):
        """Open a live display; close the window to stop.

        Parameters
        ----------
        interval : int, optional
            Milliseconds between frames (default 30).
        """
        import matplotlib.pyplot as plt
        from matplotlib.animation import FuncAnimation

        fig, ax = plt.subplots(num=repr(self))
        img = ax.imshow(self._state, cmap='viridis', vmin=0, vmax=1,
                        interpolation='nearest')
        ax.set_axis_off()

        def step(_):
            self.evolve()
            img.set_data(self._state)
            return (img,)

        animation = FuncAnimation(fig, step, interval=interval,
                                  cache_frame_data=False)
        plt.show()
        return animation

    #------------------------------------------------------------ internals
    @staticmethod
    def _count_mask(counts):
        counts = np.asarray(counts, dtype=int)
        if counts.size and (counts.min() < 0 or counts.max() > 8):
            raise ValueError('neighbor counts must lie in 0-8')
        mask = np.zeros(9, dtype=bool)
        mask[counts] = True
        return mask

    @staticmethod
    def _neighbor_counts(state):
        """Moore-neighborhood sums with periodic wrapping."""
        counts = np.zeros(state.shape, dtype=np.uint8)
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                counts += np.roll(state, (dr, dc), axis=(0, 1))
        return counts

    def _remember(self, state):
        self._history.append(state.copy())
        if len(self._history) > self.memory:
            del self._history[0]

    def __repr__(self):
        b = ''.join(str(i) for i in np.flatnonzero(self._births))
        s = ''.join(str(i) for i in np.flatnonzero(self._survivals))
        return 'CA2D(B%s/S%s, shape=%s)' % (b, s, repr(self.shape))
