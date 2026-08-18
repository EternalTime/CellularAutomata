Applet
======

.. raw:: html

   <link rel="stylesheet" href="_static/ca_applet.css">
   <div id="ca-app"></div>
   <script src="_static/ca_applet.js"></script>

The library, running live in your browser. The update rules are the same
ones pyCA applies in Python - the lookup-table step of :class:`pyCA.ECA`,
the flipped outputs of :class:`pyCA.NoisyECA`, the broken clock of
:class:`pyCA.AsyncECA`, the heat-bath flips of :class:`pyCA.ICA`, and the
outer-totalistic B/S counts of :class:`pyCA.CA2D` - ported line for line
from the modules they document. Nothing is precomputed: the spacetime
diagram scrolling past is the history of an automaton being run as you
watch.

The applet is yours to take apart. It ships with the library as
`docs/_static/ca_applet.js
<https://github.com/EternalTime/CellularAutomata/blob/main/docs/_static/ca_applet.js>`_:
plain JavaScript with no build step and no dependencies, of which the first
half is the library itself - the rules and the measures, function for
function - and the rest is scenery.

The square panel plots the normalized Lempel--Ziv
complexity\ :footcite:`lempel1976` of
:func:`pyCA.measures.lz_complexity` against
:func:`pyCA.measures.entropy_rate` with :math:`k = 2`, computed on the
current state at every step, on equal axes. Both axes estimate the entropy
rate - :math:`h_2` sees only pair correlations, :math:`C_{LZ}` regularity at
every length - so the diagonal is the reference, and the plot locates a rule
on Wolfram's spectrum at a glance. A frozen rule pins both measures to zero.
A chaotic rule like 30 rides the top right corner, since each new cell is a
fresh coin flip even knowing its neighbor. A structured rule is the
interesting case: rule 110 sags below the diagonal, the gap being exactly
the structure longer than two cells that only the parse can see, the
particles and the periodic background they travel through.

The stochastic variants put a dial on that distinction. Feed rule 110 a
little noise and watch :math:`h_2` climb toward the coin-flip ceiling as
the correlations are eaten; slow the asynchronous clock and watch structure
survive surprisingly far. The Ising automaton stages the competition
directly: at low temperature the heat bath *orders* the lattice and both
meters fall; at high temperature it randomizes, and the rule fights to keep
:math:`h_2` down. For the two-dimensional family, type neighbor counts into
the B and S boxes. Life is B3/S23, and the meters read its thin ash of
still lifes and gliders as low entropy over a mostly empty lattice.

References
^^^^^^^^^^

.. footbibliography::
