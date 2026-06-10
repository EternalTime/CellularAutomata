"""Elementary cellular automata.

An elementary cellular automaton (ECA) is the simplest interesting dynamical
system there is: a periodic row of cells, each 0 or 1, each updating from its
own value and its two neighbors' values according to one of the 256 possible
rules. Stephen Wolfram's numbering names each rule by the byte whose bit n
gives the output for the neighborhood whose (left, center, right) values
read, as a binary number, n.

The :class:`ECA` class mirrors the original MATLAB implementation: ``rule``
and ``state`` are validated properties that can be reassigned at any time,
``evolve`` advances one step, and ``play`` opens a live spacetime display.
"""

import numpy as np

class ECA:
    """A 1-dimensional elementary cellular automaton on a periodic lattice.

    Parameters
    ----------
    rule : int
        Wolfram rule number, 0-255.
    state : array_like of 0s and 1s, optional
        Initial state. If omitted, a random state of length `N` is drawn.
    N : int, optional
        Lattice size used when `state` is omitted (default 64).
    memory : int, optional
        Number of past states retained for `spacetime` and `play`. Defaults
        to max(min(3*N, 5000), 300), matching the MATLAB class.
    rng : numpy.random.Generator, optional
        Random source; defaults to ``numpy.random.default_rng()``.

    Attributes
    ----------
    rule : int
        The rule number. Reassigning it rebuilds the lookup table.
    state : ndarray
        The current state. Reassigning it appends to the history.
    N : int
        Lattice size.

    Examples
    --------
    >>> from pyCA import ECA
    >>> ca = ECA(110, N=128)
    >>> ca.run(100)
    >>> ca.spacetime().shape
    (101, 128)
    """

    def __init__(self, rule, state=None, N=64, memory=None, rng=None):
        self._rng = rng if rng is not None else np.random.default_rng()
        if state is None:
            state = self._rng.integers(0, 2, N)
        state = np.asarray(state)
        self.N = state.size
        self.memory = (memory if memory is not None
                       else max(min(3*self.N, 5000), 300))
        self._history = []
        self.state = state          # validated; appends to history
        self.rule = rule            # validated; builds the lookup table

    #------------------------------------------------ validated properties
    @property
    def rule(self):
        return self._rule

    @rule.setter
    def rule(self, newRule):
        if newRule != int(newRule) or not (0 <= newRule <= 255):
            raise ValueError('rule must be an integer between 0 and 255')
        self._rule = int(newRule)
        #bit n of the rule is the output for neighborhood number n
        self._ruleArray = np.array([(self._rule >> n) & 1 for n in range(8)],
                                   dtype=np.uint8)

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, newState):
        newState = np.asarray(newState)
        if newState.ndim != 1 or not np.isin(newState, [0, 1]).all():
            raise ValueError('state must be a 1d array of 0s and 1s')
        if hasattr(self, '_state') and newState.size != self.N:
            raise ValueError('state must keep its length %d' % self.N)
        self._state = newState.astype(np.uint8)
        self._remember(self._state)

    #------------------------------------------------------------ dynamics
    def evolve(self):
        """Advance the automaton one time step."""
        self.state = self._apply_rule(self._state)

    def run(self, steps):
        """Advance the automaton `steps` time steps."""
        for _ in range(steps):
            self.evolve()

    def spacetime(self):
        """The remembered history as a (time, space) array of 0s and 1s.

        Row 0 is the oldest remembered state; the last row is the current
        state. At most `memory` rows are kept.
        """
        return np.array(self._history)

    def play(self, interval=30):
        """Open a live spacetime display; close the window to stop.

        Parameters
        ----------
        interval : int, optional
            Milliseconds between frames (default 30).
        """
        import matplotlib.pyplot as plt
        from matplotlib.animation import FuncAnimation

        fig, ax = plt.subplots(num='Rule %d' % self.rule)
        img = ax.imshow(self.spacetime(), cmap='viridis', vmin=0, vmax=1,
                        aspect='auto', interpolation='nearest')
        ax.set_axis_off()

        def step(_):
            self.evolve()
            data = self.spacetime()
            img.set_data(data)
            img.set_extent((-.5, self.N - .5, data.shape[0] - .5, -.5))
            return (img,)

        animation = FuncAnimation(fig, step, interval=interval,
                                  cache_frame_data=False)
        plt.show()
        return animation

    #------------------------------------------------------------ internals
    def _apply_rule(self, state):
        """One synchronous update: neighborhood number, then table lookup."""
        idx = (4*np.roll(state, 1) + 2*state + np.roll(state, -1))
        return self._ruleArray[idx]

    def _remember(self, state):
        self._history.append(state.copy())
        if len(self._history) > self.memory:
            del self._history[0]

    def __repr__(self):
        return '%s(rule=%d, N=%d)' % (type(self).__name__, self.rule, self.N)
