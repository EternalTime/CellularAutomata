"""Probabilistic elementary cellular automata beyond the Ising family.

Two ways of corrupting a deterministic rule with noise. :class:`NoisyECA`
applies the rule everywhere and then flips each output bit independently
with probability `noise` — the epsilon-perturbed CAs whose phase transitions
have been studied since Wolfram's classification. :class:`AsyncECA` keeps
the rule exact but breaks the synchronous clock: each step, only a random
fraction of the cells update, the rest holding their values. Both reduce to
the deterministic :class:`pyCA.eca.ECA` in the appropriate limit (noise = 0,
update_fraction = 1), and the tests hold them to it.
"""

import numpy as np
from pyCA.eca import ECA

class NoisyECA(ECA):
    """An ECA whose outputs are flipped independently with probability `noise`.

    Parameters
    ----------
    rule : int
        Wolfram rule number, 0-255.
    state : array_like of 0s and 1s, optional
        Initial state. If omitted, a random state of length `N` is drawn.
    noise : float, optional
        Per-cell, per-step probability of flipping the rule's output
        (default 0). noise = 0 is the deterministic rule; noise = 1 is the
        complemented rule; noise = 0.5 is coin flipping, with the rule
        forgotten entirely.
    N, memory, rng
        As for :class:`pyCA.eca.ECA`.
    """

    def __init__(self, rule, state=None, noise=0.0, N=64, memory=None,
                 rng=None):
        super().__init__(rule, state, N=N, memory=memory, rng=rng)
        self.noise = noise

    @property
    def noise(self):
        return self._noise

    @noise.setter
    def noise(self, newNoise):
        if not 0 <= newNoise <= 1:
            raise ValueError('noise must lie in [0, 1]')
        self._noise = float(newNoise)

    def evolve(self):
        """Apply the rule, then flip each output with probability `noise`."""
        state = self._apply_rule(self._state)
        flips = self._rng.random(self.N) < self._noise
        state[flips] = 1 - state[flips]
        self.state = state


class AsyncECA(ECA):
    """An ECA updated asynchronously: only a random fraction moves per step.

    Each step, every cell independently chooses (with probability
    `update_fraction`) whether to apply the rule to its current
    neighborhood; cells that decline keep their value. The rule itself is
    never corrupted — only the synchronous clock is.

    Parameters
    ----------
    rule : int
        Wolfram rule number, 0-255.
    state : array_like of 0s and 1s, optional
        Initial state. If omitted, a random state of length `N` is drawn.
    update_fraction : float, optional
        Per-cell, per-step probability of updating (default 1, which is
        the synchronous ECA; 0 freezes the lattice).
    N, memory, rng
        As for :class:`pyCA.eca.ECA`.
    """

    def __init__(self, rule, state=None, update_fraction=1.0, N=64,
                 memory=None, rng=None):
        super().__init__(rule, state, N=N, memory=memory, rng=rng)
        self.update_fraction = update_fraction

    @property
    def update_fraction(self):
        return self._update_fraction

    @update_fraction.setter
    def update_fraction(self, newFraction):
        if not 0 <= newFraction <= 1:
            raise ValueError('update_fraction must lie in [0, 1]')
        self._update_fraction = float(newFraction)

    def evolve(self):
        """Update a random fraction of the cells; the rest stand still."""
        updates = self._rng.random(self.N) < self._update_fraction
        state = self._state.copy()
        state[updates] = self._apply_rule(self._state)[updates]
        self.state = state
