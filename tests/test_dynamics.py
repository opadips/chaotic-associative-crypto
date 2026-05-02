import numpy as np
from network import ChaoticOscillatoryNetwork
from dynamics import lyapunov_exponent, divergence_curve, entropy, autocorrelation
from crypto import CAMCCipher
from associative import store_patterns_hebbian

def test_lyapunov_positive():
    n = 64
    net = ChaoticOscillatoryNetwork(n_neurons=n, weight_scale=2.0)
    state = np.exp(1j * np.random.uniform(0, 2 * np.pi, n))
    lle = lyapunov_exponent(net, state, steps=300, delta=1e-6)
    assert lle > 0.0

def test_divergence_grows():
    n = 64
    net = ChaoticOscillatoryNetwork(n_neurons=n, weight_scale=2.0)
    state_a = np.exp(1j * np.random.uniform(0, 2 * np.pi, n))
    state_b = state_a.copy()
    state_b[0] *= np.exp(1j * 1e-4)
    distances = divergence_curve(net, state_a, state_b, steps=200)
    assert distances[-1] > distances[0] * 100

def test_entropy_high_for_ciphertext():
    n = 64
    net = ChaoticOscillatoryNetwork(n_neurons=n, weight_scale=2.0)
    sync = np.exp(1j * np.random.uniform(0, 2 * np.pi, n))
    cipher = CAMCCipher(net, sync)
    plaintext = "A" * 500
    encrypted = cipher.encrypt(plaintext)
    h = entropy(encrypted)
    assert h > 7.0

def test_autocorrelation_low_for_lag_one():
    n = 64
    net = ChaoticOscillatoryNetwork(n_neurons=n, weight_scale=2.0)
    sync = np.exp(1j * np.random.uniform(0, 2 * np.pi, n))
    cipher = CAMCCipher(net, sync)
    plaintext = "B" * 500
    encrypted = cipher.encrypt(plaintext)
    ac = autocorrelation(encrypted, max_lag=5)
    assert abs(ac[1]) < 0.3