"""Tests pinning the physics of pyCA to known results."""

import numpy as np
import pytest

from pyCA import ECA, ICA, NoisyECA, AsyncECA, CA2D, measures


#---------------------------------------------------------------------- ECA
def brute_force_step(rule, state):
    """Reference ECA update: explicit loop, no cleverness."""
    bits = [(rule >> n) & 1 for n in range(8)]
    N = len(state)
    return np.array([bits[4*state[(i - 1) % N] + 2*state[i]
                          + state[(i + 1) % N]] for i in range(N)],
                    dtype=np.uint8)

def test_eca_matches_brute_force():
    rng = np.random.default_rng(0)
    for rule in rng.integers(0, 256, 20):
        ca = ECA(int(rule), rng.integers(0, 2, 65))
        expected = brute_force_step(int(rule), ca.state)
        ca.evolve()
        assert np.array_equal(ca.state, expected)

def test_rule_90_is_xor_of_neighbors():
    state = np.zeros(101, dtype=int)
    state[50] = 1
    ca = ECA(90, state)
    for _ in range(40):
        prev = ca.state.copy()
        ca.evolve()
        assert np.array_equal(ca.state,
                              np.roll(prev, 1) ^ np.roll(prev, -1))

def test_rule_204_is_identity():
    ca = ECA(204, N=64, rng=np.random.default_rng(1))
    before = ca.state.copy()
    ca.run(10)
    assert np.array_equal(ca.state, before)

def test_rules_0_and_255():
    ca = ECA(0, N=32, rng=np.random.default_rng(2))
    ca.evolve()
    assert not ca.state.any()
    ca = ECA(255, N=32, rng=np.random.default_rng(3))
    ca.evolve()
    assert ca.state.all()

def test_spacetime_shape_and_memory():
    ca = ECA(110, N=16, memory=10)
    ca.run(50)
    st = ca.spacetime()
    assert st.shape == (10, 16)
    assert np.array_equal(st[-1], ca.state)

def test_validation():
    with pytest.raises(ValueError):
        ECA(256, N=8)
    with pytest.raises(ValueError):
        ECA(-1, N=8)
    with pytest.raises(ValueError):
        ECA(30, [0, 1, 2])


#---------------------------------------------------------------------- ICA
def test_ica_stochfrac_zero_reduces_to_eca():
    rng = np.random.default_rng(4)
    state = rng.integers(0, 2, 64)
    ica = ICA(110, state.copy(), temperature=1.0, stochfrac=0.0)
    eca = ECA(110, state.copy())
    for _ in range(20):
        ica.evolve()
        eca.evolve()
        assert np.array_equal(ica.state, eca.state)

def test_ica_energy_bounds():
    #per-site Ising energy of the +/-1 chain lies in [-1, 1]
    ica = ICA(30, N=128, temperature=2.0, stochfrac=0.8,
              rng=np.random.default_rng(5))
    for _ in range(20):
        ica.evolve()
        assert -1.0 <= ica.energy <= 1.0

def test_ica_cold_aligned_chain_is_stable():
    #at T ~ 0, a fully aligned chain has no frustrated cells: no flips
    state = np.ones(64, dtype=int)
    ica = ICA(204, state, temperature=0.0, stochfrac=1.0,
              rng=np.random.default_rng(6))
    ica.run(20)
    assert ica.state.all()


#--------------------------------------------------------------- stochastic
def test_noisy_eca_limits():
    rng = np.random.default_rng(7)
    state = rng.integers(0, 2, 64)
    quiet = NoisyECA(110, state.copy(), noise=0.0)
    eca = ECA(110, state.copy())
    quiet.evolve(); eca.evolve()
    assert np.array_equal(quiet.state, eca.state)

    loud = NoisyECA(110, state.copy(), noise=1.0)
    eca2 = ECA(110, state.copy())
    loud.evolve(); eca2.evolve()
    assert np.array_equal(loud.state, 1 - eca2.state)

def test_async_eca_limits():
    rng = np.random.default_rng(8)
    state = rng.integers(0, 2, 64)
    sync = AsyncECA(30, state.copy(), update_fraction=1.0)
    eca = ECA(30, state.copy())
    sync.evolve(); eca.evolve()
    assert np.array_equal(sync.state, eca.state)

    frozen = AsyncECA(30, state.copy(), update_fraction=0.0)
    frozen.run(10)
    assert np.array_equal(frozen.state, state)


#--------------------------------------------------------------------- CA2D
def brute_force_life_step(state):
    rows, cols = state.shape
    new = np.zeros_like(state)
    for r in range(rows):
        for c in range(cols):
            n = sum(state[(r + dr) % rows, (c + dc) % cols]
                    for dr in (-1, 0, 1) for dc in (-1, 0, 1)
                    if (dr, dc) != (0, 0))
            if state[r, c] == 1:
                new[r, c] = 1 if n in (2, 3) else 0
            else:
                new[r, c] = 1 if n == 3 else 0
    return new

def test_life_matches_brute_force():
    rng = np.random.default_rng(9)
    life = CA2D.life(state=rng.integers(0, 2, (20, 20)))
    expected = brute_force_life_step(life.state)
    life.evolve()
    assert np.array_equal(life.state, expected)

def test_glider_translates():
    state = np.zeros((20, 20), dtype=int)
    #the standard glider
    glider = [(0, 1), (1, 2), (2, 0), (2, 1), (2, 2)]
    for r, c in glider:
        state[r + 5, c + 5] = 1
    life = CA2D.life(state=state)
    life.run(4)
    assert np.array_equal(life.state, np.roll(state, (1, 1), axis=(0, 1)))

def test_blinker_period_two():
    state = np.zeros((9, 9), dtype=int)
    state[4, 3:6] = 1
    life = CA2D.life(state=state)
    life.run(2)
    assert np.array_equal(life.state, state)

def test_block_is_still():
    state = np.zeros((8, 8), dtype=int)
    state[3:5, 3:5] = 1
    life = CA2D.life(state=state)
    life.run(5)
    assert np.array_equal(life.state, state)


#----------------------------------------------------------------- measures
def test_entropy_of_uniform_lattice_is_zero():
    assert measures.block_entropy(np.zeros(100, dtype=int), k=3) == 0.0
    assert measures.block_entropy(np.ones((10, 50), dtype=int), k=2) == 0.0

def test_entropy_of_fair_coins_is_one_bit():
    rng = np.random.default_rng(10)
    data = rng.integers(0, 2, (200, 200))
    assert abs(measures.block_entropy(data, k=1) - 1.0) < 1e-3
    assert abs(measures.entropy_rate(data, k=4) - 1.0) < 1e-2

def test_entropy_rate_of_dead_rule_is_zero():
    ca = ECA(0, N=64, rng=np.random.default_rng(11))
    ca.run(100)
    assert measures.entropy_rate(ca.spacetime()[5:], k=3) == 0.0

def test_block_entropy_monotone_in_k():
    ca = ECA(30, N=256, rng=np.random.default_rng(12))
    ca.run(200)
    st = ca.spacetime()
    hs = [measures.block_entropy(st, k) for k in (1, 2, 3, 4)]
    assert all(b >= a - 1e-12 for a, b in zip(hs, hs[1:]))

def test_mutual_information_limits():
    rng = np.random.default_rng(13)
    #independent fair coins: MI ~ 0
    data = rng.integers(0, 2, (300, 300))
    assert measures.mutual_information(data, 1) < 1e-2
    #perfectly correlated neighbors (constant rows of alternating blocks)
    data = np.tile(rng.integers(0, 2, (300, 1)), (1, 50))
    mi = measures.mutual_information(data, 1)
    h1 = measures.block_entropy(data, 1)
    assert abs(mi - h1) < 1e-12
