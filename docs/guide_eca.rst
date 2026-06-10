Elementary Cellular Automata
============================

An elementary cellular automaton is a row of cells, each 0 or 1, each
updating simultaneously from its own value and its two nearest neighbors'.
That is the entire specification — three binary inputs, one binary output —
yet the 256 possible update tables exhaust an astonishing range of behavior.
Stephen Wolfram's numbering scheme names each table by a single byte: bit
:math:`n` of the rule number is the output for the neighborhood whose
(left, center, right) values, read as a binary number, equal :math:`n`.
Rule 90, for instance, is 01011010 in binary — work through the eight
neighborhoods and convince yourself it computes left XOR right.

Driving the class
^^^^^^^^^^^^^^^^^

The :class:`pyCA.eca.ECA` class keeps the original MATLAB interface: `rule`
and `state` are validated properties you can reassign mid-flight, `evolve`
advances one step, and `play` opens a live display. The Python class adds
`run` and `spacetime`::

    from pyCA import ECA

    ca = ECA(110, N=256)      # random initial state on 256 cells
    ca.run(300)
    history = ca.spacetime()  # (time, space) array, newest row last

    ca.rule = 90              # swap the rule; the state carries over
    ca.run(300)

States live on a periodic lattice — the row is a ring — so boundary effects
never contaminate the dynamics, though patterns that outrun the lattice will
meet themselves coming around.

The four classes
^^^^^^^^^^^^^^^^

Wolfram's classification sorts the rules by what they do to almost any
initial condition. Class I rules freeze into uniformity (rule 0, rule 255).
Class II rules settle into stripes or simple periodic textures (rule 204,
the identity, is the laziest member). Class III rules churn out apparent
randomness forever — rule 30 is the archetype. Class IV rules live on the
boundary, supporting localized structures that move and collide — rule 110,
famously, is Turing complete: Matthew Cook proved in the 1990s that those
colliding gliders can simulate any computation.

Survey them yourself::

    import matplotlib.pyplot as plt
    from pyCA import ECA

    rules = [255, 204, 30, 110]
    fig, axes = plt.subplots(2, 2, figsize=(10, 8))
    for rule, ax in zip(rules, axes.flat):
        ca = ECA(rule, N=256)
        ca.run(256)
        ax.imshow(ca.spacetime(), cmap='binary', interpolation='nearest')
        ax.set_title('Rule %d' % rule)
        ax.set_axis_off()
    plt.show()

Pick a handful of rules at random and classify them by eye before reading
their known classes — the boundaries are blurrier than the taxonomy
suggests, and deciding where a rule belongs is a better teacher than being
told. Then come back with :doc:`guide_measures` and classify them by number
instead.
