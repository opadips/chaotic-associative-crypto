import numpy as np
import pytest
from network import ChaoticOscillatoryNetwork
from block_cipher import CAMCBlockCipher

def test_encrypt_decrypt_roundtrip():
    n_neurons = 128
    net = ChaoticOscillatoryNetwork(n_neurons=n_neurons, weight_scale=1.5)
    cipher = CAMCBlockCipher(net, rounds=12, steps_per_round=3)
    plaintext = b"A" * 64
    encrypted = cipher.encrypt(plaintext)
    decrypted = cipher.decrypt(encrypted)
    assert decrypted == plaintext

def test_avalanche_effect():
    n_neurons = 128
    net = ChaoticOscillatoryNetwork(n_neurons=n_neurons, weight_scale=1.5)
    cipher = CAMCBlockCipher(net, rounds=12, steps_per_round=3)
    p1 = b"A" * 64
    p2 = bytearray(p1)
    p2[0] ^= 0x01
    p2 = bytes(p2)
    c1 = cipher.encrypt(p1)
    c2 = cipher.encrypt(p2)
    diff = sum(bin(a ^ b).count('1') for a, b in zip(c1, c2))
    total_bits = len(c1) * 8
    ratio = diff / total_bits
    assert 0.4 < ratio < 0.6

def test_tamper_detection_fails():
    n_neurons = 128
    net = ChaoticOscillatoryNetwork(n_neurons=n_neurons, weight_scale=1.5)
    cipher = CAMCBlockCipher(net, rounds=12, steps_per_round=3)
    plaintext = b"A" * 64
    encrypted = cipher.encrypt(plaintext)
    tampered = bytearray(encrypted)
    tampered[10] ^= 0xFF
    tampered = bytes(tampered)
    decrypted = cipher.decrypt(tampered)
    assert decrypted != plaintext

def test_integrity_pattern_roundtrip():
    n_neurons = 128
    net = ChaoticOscillatoryNetwork(n_neurons=n_neurons, weight_scale=1.5)
    cipher = CAMCBlockCipher(net, rounds=12, steps_per_round=3)
    pattern = b"CHKSUM1234CHECKSABCDEFGHIJKLMNOP"
    cipher.set_integrity_pattern(pattern)
    msg_32 = b"A" * 32
    encrypted = cipher.encrypt(msg_32)
    decrypted = cipher.decrypt(encrypted)
    assert decrypted == msg_32

def test_integrity_detects_tamper():
    n_neurons = 128
    net = ChaoticOscillatoryNetwork(n_neurons=n_neurons, weight_scale=1.5)
    cipher = CAMCBlockCipher(net, rounds=12, steps_per_round=3)
    pattern = b"CHKSUM1234CHECKSABCDEFGHIJKLMNOP"
    cipher.set_integrity_pattern(pattern)
    msg_32 = b"A" * 32
    encrypted = cipher.encrypt(msg_32)
    tampered = bytearray(encrypted)
    tampered[10] ^= 0xFF
    tampered = bytes(tampered)
    with pytest.raises(ValueError, match="Integrity check failed"):
        cipher.decrypt(tampered)