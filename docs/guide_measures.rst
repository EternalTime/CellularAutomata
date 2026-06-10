Information Measures
====================

Describe a spacetime diagram cell by cell and you have described it
completely — and learned almost nothing. The complete description is mostly
data with very little information. The measures in
:mod:`pyCA.measures` compress the data into the few numbers that matter:
how unpredictable is a cell, how far do correlations reach, how many new
bits does each cell carry once its neighbors are known. All entropies are
in bits, and every function accepts either a single state or a full
spacetime history (time along axis 0).

Block entropy
^^^^^^^^^^^^^

Slide a window of length :math:`k` along each row, histogram the
:math:`2^k` possible words, and take the Shannon entropy of the result —
that is :math:`H_k`, the block entropy. For a frozen lattice it vanishes;
for fair coin flips it equals :math:`k`; everything interesting lies
between, and the *gap* below :math:`k` measures the structure the automaton
has built. ::

    from pyCA import ECA, measures

    ca = ECA(30, N=512)
    ca.run(500)
    st = ca.spacetime()

    for k in (1, 2, 3, 4, 5):
        print(k, measures.block_entropy(st, k))

:math:`H_k` never decreases with :math:`k` — prove this to yourself from
the definition before trusting the code, which is tested for it.

Entropy rate
^^^^^^^^^^^^

The increments :math:`h_k = H_k - H_{k-1}` converge from above to the
entropy rate: the number of genuinely new bits per cell once a cell's
context is known. The entropy rate is the honest measure of randomness —
rule 90's spacetime diagram looks busy, but knowing two cells pins the
third, and the rate reveals the redundancy. ::

    print(measures.entropy_rate(st, k=5))

One practical warning: estimating :math:`H_k` needs enough samples to
populate :math:`2^k` bins. Keep :math:`2^k` comfortably below the number of
cells in your history or the estimate biases low.

Mutual information
^^^^^^^^^^^^^^^^^^

:func:`pyCA.measures.mutual_information` asks how much knowing one cell
tells you about a cell `distance` sites away — :math:`I(X;Y) = H(X) + H(Y)
- H(X,Y)`, pooled over every pair at that separation. Zero means
independence; the maximum, :math:`H(X)`, means determination. Plotted
against distance it is a correlation function with information-theoretic
units::

    import matplotlib.pyplot as plt

    ds = range(1, 30)
    plt.plot(ds, [measures.mutual_information(st, d) for d in ds])
    plt.xlabel('distance')
    plt.ylabel('I (bits)')
    plt.show()

A classification experiment
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Wolfram's four classes were assigned by eye. Assign them by number instead:
for each rule in a sample, run a random initial condition, discard the
transient, and place the rule on the (entropy rate, mutual information)
plane. Class I collapses to the origin, Class III crowds the high-rate
edge, and Class IV — the computing class — lives where the entropy rate is
moderate but the mutual information refuses to die. There is a lot of
unexplored territory in that plane; keep a journal of what you find in it.
