pyCA
====

In the 1940s at Los Alamos, Stanislaw Ulam was growing crystal patterns on a
lattice while John von Neumann hunted for a machine that could build a copy
of itself; Ulam suggested the lattice, and the cellular automaton was born.
John Conway made the subject a household game in 1970 when Martin Gardner's
column unveiled the Game of Life, and Stephen Wolfram made it a science in
the 1980s by numbering the 256 elementary rules and sorting their behaviors
into classes — frozen, periodic, chaotic, and the strange fourth class that
computes. The lesson of that lineage is the lesson of this library: a rule
you can write on one line can produce a history you cannot compress at all.

pyCA builds those histories and measures them. The automata span the
deterministic elementary rules, an Ising variant where a rule competes with
a heat bath, noisy and asynchronous corruptions of the synchronous clock,
and outer-totalistic two-dimensional rules with Life as the standard-bearer.
The measures — block entropy, entropy rate, mutual information — quantify
how much information a spacetime diagram carries, and where it lives.

If you're new here, start with :doc:`getting_started`, then work through
whichever guide matches your problem. The original 2016 MATLAB classes are
preserved in the repository's ``matlab/`` directory.

Guide
^^^^^

.. toctree::
   :maxdepth: 1

   getting_started
   guide_eca
   guide_stochastic
   guide_life
   guide_measures

Reference
^^^^^^^^^

.. toctree::
   :maxdepth: 2

   api/pyCA
   license

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
