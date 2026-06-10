"""Ising cellular automata: deterministic rules with thermal noise.

An Ising cellular automaton (ICA) couples two dynamics on the same periodic
lattice. A fraction of the cells, drawn fresh at random each step, evolve
stochastically as Ising spins in contact with a heat bath — a cell flips
with the heat-bath probability determined by its local Ising energy and the
temperature. The remaining cells evolve deterministically by an elementary
cellular automaton rule. With stochfrac = 0 the ICA reduces exactly to the
underlying :class:`pyCA.eca.ECA`; with stochfrac = 1 it is a kinetic Ising
chain; in between, determinism and thermal noise compete.
"""

import numpy as np
from pyCA.eca import ECA

class ICA(ECA):
    """A 1-dimensional Ising cellular automaton.

    Parameters
    ----------
    rule : int
        Wolfram rule number, 0-255, governing the deterministic cells.
    state : array_like of 0s and 1s, optional
        Initial state. If omitted, a random state of length `N` is drawn.
    temperature : float, optional
        Heat-bath temperature for the stochastic cells (default 1).
    stochfrac : float, optional
        Probability for each cell, each step, to evolve stochastically
        instead of deterministically (default 0.5).
    N, memory, rng
        As for :class:`pyCA.eca.ECA`.

    Attributes
    ----------
    energy : float
        Mean Ising energy per site of the current state, updated at each
        `evolve` call.
    temperature : float
        Validated property; reassign freely (an epsilon regularizes T = 0).
    stochfrac : float
        Validated property, in [0, 1].
    """

    def __init__(self, rule, state=None, temperature=1.0, stochfrac=0.5,
                 N=64, memory=None, rng=None):
        super().__init__(rule, state, N=N, memory=memory, rng=rng)
        self.temperature = temperature
        self.stochfrac = stochfrac
        self.energy = np.mean(self._state_energy())

    #------------------------------------------------ validated properties
    @property
    def temperature(self):
        return self._temperature

    @temperature.setter
    def temperature(self, newTemperature):
        if newTemperature < 0:
            raise ValueError('temperature must be nonnegative')
        self._temperature = float(newTemperature)
        self._invT = 1.0/(np.finfo(float).eps + self._temperature)

    @property
    def stochfrac(self):
        return self._stochfrac

    @stochfrac.setter
    def stochfrac(self, newStochFrac):
        if not 0 <= newStochFrac <= 1:
            raise ValueError('stochfrac must lie in [0, 1]')
        self._stochfrac = float(newStochFrac)

    #------------------------------------------------------------ dynamics
    def evolve(self):
        """Advance one step: thermal flips where chosen, the rule elsewhere."""
        stochCellIdx = np.flatnonzero(
            self._rng.random(self.N) < self._stochfrac)
        stochCellVal = self._state[stochCellIdx].copy()
        stateEnergy = self._state_energy()
        self.energy = np.sum(stateEnergy)/self.N
        flippedIdx = self._stoch_evolve(stateEnergy[stochCellIdx])
        stochCellVal[flippedIdx] = 1 - stochCellVal[flippedIdx]
        state = self._apply_rule(self._state)
        state[stochCellIdx] = stochCellVal
        self.state = state

    #------------------------------------------------------------ internals
    def _state_energy(self):
        """Per-site Ising energy, -s_i (s_{i-1} + s_{i+1})/2 with s = +/-1."""
        isingArray = 2.0*self._state - 1.0
        stateEnergy = .5*(np.roll(isingArray, 1) + np.roll(isingArray, -1))
        return -isingArray*stateEnergy

    def _stoch_evolve(self, stateEnergy):
        """Heat-bath flips: cell i flips with probability 1/(1+e^(-2*E_i/T)).

        High-energy (frustrated) cells flip eagerly; low-energy (aligned)
        cells flip reluctantly, and not at all as T -> 0.
        """
        #clipping the exponent avoids a harmless overflow warning at T ~ 0
        x = np.clip(2.0*self._invT*stateEnergy, -700.0, 700.0)
        return np.flatnonzero(
            self._rng.random(stateEnergy.size) < 1.0/(1.0 + np.exp(-x)))
