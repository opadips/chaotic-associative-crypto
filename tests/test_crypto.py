import numpy as np
from network import ChaoticOscillatoryNetwork
from associative import store_patterns_hebbian
from crypto import CAMCCipher

def test_encrypt_decrypt_roundtrip():
    n = 64
    network = ChaoticOscillatoryNetwork(n_neurons=n)
    patterns = [np.exp(1j * np.random.uniform(0, 2 * np.pi, n))]
    store_patterns_hebbian(network, patterns, alpha=0.05)
    sync_state = np.exp(1j * np.random.uniform(0, 2 * np.pi, n))
    cipher = CAMCCipher(network, sync_state)
    plaintext = "This is a secret message for CAMC testing."
    encrypted = cipher.encrypt(plaintext)
    decrypted = cipher.decrypt(encrypted)
    assert decrypted == plaintext

def test_wrong_sync_state_fails():
    n = 64
    network = ChaoticOscillatoryNetwork(n_neurons=n)
    sync_state = np.exp(1j * np.random.uniform(0, 2 * np.pi, n))
    wrong_sync = np.exp(1j * np.random.uniform(0, 2 * np.pi, n))
    cipher = CAMCCipher(network, sync_state)
    cipher_wrong = CAMCCipher(network, wrong_sync)
    plaintext = "Sensitive data"
    encrypted = cipher_wrong.encrypt(plaintext)
    decrypted = cipher.decrypt(encrypted)
    assert decrypted != plaintext

def test_bit_flip_avalanche():
    n = 64
    network = ChaoticOscillatoryNetwork(n_neurons=n)
    sync_state = np.exp(1j * np.random.uniform(0, 2 * np.pi, n))
    cipher = CAMCCipher(network, sync_state)
    text_a = "aaaa"
    text_b = "aaab"
    enc_a = cipher.encrypt(text_a)
    enc_b = cipher.encrypt(text_b)
    diff_count = sum(1 for a, b in zip(enc_a, enc_b) if a != b)
    assert diff_count > 0