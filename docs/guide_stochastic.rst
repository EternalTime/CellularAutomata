Thermal and Stochastic Automata
===============================

A deterministic rule is an idealization; real systems shake. The three
classes here corrupt the elementary automata in physically distinct ways,
and each reduces exactly to the clean :class:`pyCA.eca.ECA` in the
appropriate limit. The tests hold them to it.

The Ising cellular automaton
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

:class:`pyCA.ica.ICA` makes the lattice a hybrid: each step, every cell
independently chooses (with probability `stochfrac`) whether to behave as an
Ising spin in contact with a heat bath or as an obedient cell of the
underlying rule. A thermal cell reads its local Ising energy and flips with
the heat-bath\ :footcite:`glauber1963` probability
:math:`1/(1 + e^{-2E_i/T})`. Frustration makes it flip eagerly; alignment
makes it hold fast, absolutely so as :math:`T \to 0`. ::

    from pyCA import ICA

    ica = ICA(110, N=256, temperature=1.5, stochfrac=0.3)
    ica.run(300)
    print(ica.energy)     # mean Ising energy per site

Sweep the temperature at fixed `stochfrac`, then `stochfrac` at fixed
temperature, and watch rule 110's gliders fight the noise. At what noise
level do they stop surviving long enough to collide? Map it out.

Noisy rules
^^^^^^^^^^^

:class:`pyCA.stochastic.NoisyECA` applies the rule everywhere, then flips
each output bit independently with probability `noise`: the
epsilon-perturbed automata. Small noise turns sharp class boundaries into
genuine phase transitions\ :footcite:`grinstein1985`; a Class II texture can
survive small epsilon and dissolve at large, with a critical point in
between. ::

    from pyCA import NoisyECA

    noisy = NoisyECA(90, N=512, noise=0.005)
    noisy.run(500)

At `noise = 0` you have the deterministic rule; at `noise = 1`, its
complement; at `noise = 0.5` the rule is forgotten entirely and every cell
is a fair coin.

Asynchronous updating
^^^^^^^^^^^^^^^^^^^^^

:class:`pyCA.stochastic.AsyncECA` never corrupts the rule, only the clock.
Each step, each cell updates with probability `update_fraction` and
otherwise holds its value. Synchrony is a strong
assumption\ :footcite:`schonfisch1999`, and some celebrated CA behaviors
lean on it harder than you might expect::

    from pyCA import AsyncECA

    lazy = AsyncECA(110, N=256, update_fraction=0.7)
    lazy.run(300)

Run rule 110 at a few update fractions and watch what survives; the gliders
that carry rule 110's computation are creatures of the synchronous clock.

References
^^^^^^^^^^

.. footbibliography::
