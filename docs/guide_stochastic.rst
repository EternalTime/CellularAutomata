Thermal and Stochastic Automata
===============================

A deterministic rule is an idealization — real systems shake. The three
classes in this guide corrupt the elementary automata in three physically
distinct ways, and each reduces exactly to the clean
:class:`pyCA.eca.ECA` in the appropriate limit. The tests in the repository
hold them to that promise.

The Ising cellular automaton
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

:class:`pyCA.ica.ICA` makes the lattice a hybrid: each step, every cell
independently chooses (with probability `stochfrac`) whether to behave as an
Ising spin in contact with a heat bath or as an obedient cell of the
underlying rule. The thermal cells look at their local Ising energy —
aligned neighbors mean low energy, frustrated neighbors mean high — and flip
with the heat-bath probability :math:`1/(1 + e^{-2E_i/T})`. Frustrated
cells flip eagerly; aligned cells hold fast, absolutely so as
:math:`T \to 0`. ::

    from pyCA import ICA

    ica = ICA(110, N=256, temperature=1.5, stochfrac=0.3)
    ica.run(300)
    print(ica.energy)     # mean Ising energy per site

Sweep the temperature at fixed `stochfrac` and watch the energy respond;
then sweep `stochfrac` at fixed temperature and watch rule 110's gliders
fight the noise. At what noise level do the gliders stop surviving long
enough to collide? That question is not rhetorical — map it out.

Noisy rules
^^^^^^^^^^^

:class:`pyCA.stochastic.NoisyECA` applies the rule everywhere, then flips
each output bit independently with probability `noise` — the
epsilon-perturbed automata. Small noise turns sharp class boundaries into
genuine phase transitions: a Class II texture can survive small epsilon and
dissolve at large, with a critical point in between. ::

    from pyCA import NoisyECA

    noisy = NoisyECA(90, N=512, noise=0.005)
    noisy.run(500)

At `noise = 0` you have the deterministic rule; at `noise = 1`, its
complement; at `noise = 0.5` the rule is forgotten entirely and every cell
is a fair coin.

Asynchronous updating
^^^^^^^^^^^^^^^^^^^^^

:class:`pyCA.stochastic.AsyncECA` never corrupts the rule — it corrupts the
clock. Each step, each cell updates with probability `update_fraction` and
otherwise holds its value. Synchrony is a strong assumption, and some
celebrated CA behaviors lean on it harder than you might expect::

    from pyCA import AsyncECA

    lazy = AsyncECA(110, N=256, update_fraction=0.7)
    lazy.run(300)

Run rule 110 at a few update fractions and watch what survives. The gliders
that carry rule 110's computation are creatures of the synchronous clock;
how gracefully they degrade is best seen with your own eyes.
