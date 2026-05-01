import numpy as np
from .network import ChaoticOscillatoryNetwork

def store_patterns_hebbian(network, patterns, alpha=0.1):
    n = network.n
    if not patterns:
        raise ValueError("patterns list is empty")
    hebbian = np.zeros((n, n), dtype=complex)
    for p in patterns:
        p = np.asarray(p, dtype=complex).ravel()
        if p.shape[0] != n:
            raise ValueError(f"pattern length {p.shape[0]} != network size {n}")
        hebbian += np.outer(p, p.conj())
    hebbian /= n
    random_part = alpha * network._generate_complex_weights()
    network.W = hebbian + random_part

def recall(network, initial_state, steps=200):
    network.evolve(steps, initial_state=initial_state)
    return network.get_state()