"""Information-theoretic measures for cellular automaton histories.

A cellular automaton is a compression problem in disguise: the rule is a few
bits, yet the spacetime diagrams range from dead uniformity to apparently
irreducible randomness. The measures here quantify where on that range a
history sits. All entropies are in bits, all distributions are estimated
empirically from the supplied data, and all functions accept either a single
state (1d array) or a spacetime history (2d array, time along axis 0) with
periodic boundaries assumed in space.
"""

import numpy as np

def block_entropy(data, k=1):
    """Shannon entropy of the length-k block distribution, in bits.

    Slides a circular window of length `k` along each row of `data`,
    histograms the resulting k-bit words over all rows and positions, and
    returns the Shannon entropy of that empirical distribution. For k = 1
    this is the entropy of the cell-value distribution; growth with k probes
    spatial correlations.

    Parameters
    ----------
    data : array_like of 0s and 1s
        A state (1d) or spacetime history (2d, time along axis 0).
    k : int, optional
        Block length (default 1).

    Returns
    -------
    float
        H_k, between 0 (uniform lattice) and k (iid coin flips).
    """
    p = _block_distribution(data, k)
    p = p[p > 0]
    return float(-np.sum(p*np.log2(p)))

def entropy_rate(data, k=2):
    """Estimate of the spatial entropy rate, H_k - H_{k-1}, in bits per cell.

    The block entropies H_k grow at most linearly in k; their increments
    converge (from above) to the entropy rate, the number of new bits each
    additional cell carries once its neighbors to one side are known. Larger
    `k` tightens the estimate but needs exponentially more data — keep
    2**k well below the number of samples.

    Parameters
    ----------
    data : array_like of 0s and 1s
        A state (1d) or spacetime history (2d, time along axis 0).
    k : int, optional
        Block length of the finer scale (default 2). Must be >= 1; k = 1
        returns H_1 itself, the rate estimate with no conditioning.

    Returns
    -------
    float
        h_k = H_k - H_{k-1}, between 0 and 1.
    """
    if k < 1:
        raise ValueError('k must be at least 1')
    if k == 1:
        return block_entropy(data, 1)
    return block_entropy(data, k) - block_entropy(data, k - 1)

def mutual_information(data, distance=1):
    """Mutual information between cells `distance` apart, in bits.

    Estimates I(X; Y) = H(X) + H(Y) - H(X, Y) where X and Y are the values
    of two cells separated by `distance` sites in the same row, pooled over
    all rows and positions (with periodic wrapping). Zero means the cells
    are statistically independent at that separation; the maximum, H(X),
    means one determines the other.

    Parameters
    ----------
    data : array_like of 0s and 1s
        A state (1d) or spacetime history (2d, time along axis 0).
    distance : int, optional
        Spatial separation between the cell pair (default 1).

    Returns
    -------
    float
        I(X; Y) >= 0.
    """
    rows = _as_rows(data)
    x = rows.ravel()
    y = np.roll(rows, -distance, axis=1).ravel()
    joint = np.zeros((2, 2))
    for a in (0, 1):
        for b in (0, 1):
            joint[a, b] = np.mean((x == a) & (y == b))
    px = joint.sum(axis=1)
    py = joint.sum(axis=0)
    info = 0.0
    for a in (0, 1):
        for b in (0, 1):
            if joint[a, b] > 0:
                info += joint[a, b]*np.log2(joint[a, b]/(px[a]*py[b]))
    return float(max(info, 0.0))

#---------------------------------------------------------------- internals
def _as_rows(data):
    data = np.asarray(data)
    if not np.isin(data, [0, 1]).all():
        raise ValueError('data must contain only 0s and 1s')
    if data.ndim == 1:
        return data[np.newaxis, :]
    if data.ndim == 2:
        return data
    raise ValueError('data must be a 1d state or 2d spacetime history')

def _block_distribution(data, k):
    rows = _as_rows(data).astype(np.int64)
    if k < 1 or k > rows.shape[1]:
        raise ValueError('block length k must lie in 1..row length')
    #encode each circular k-block as an integer word
    words = np.zeros(rows.shape, dtype=np.int64)
    for j in range(k):
        words = 2*words + np.roll(rows, -j, axis=1)
    counts = np.bincount(words.ravel(), minlength=2**k)
    return counts/counts.sum()
