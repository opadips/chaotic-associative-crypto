import numpy as np
from network import ChaoticOscillatoryNetwork
from encoding import bits_to_state, state_to_bits
from associative import store_patterns_hebbian, recall

class CAMCBlockCipher:
    def __init__(self, network, rounds=12, steps_per_round=1):
        self.network = network
        self.rounds = rounds
        self.steps_per_round = steps_per_round
        self.block_size_bytes = 64
        self.block_size_bits = self.block_size_bytes * 8
        self.integrity_pattern = None

    def set_integrity_pattern(self, pattern_bytes):
        if len(pattern_bytes) != 32:
            raise ValueError("Integrity pattern must be 32 bytes")
        pattern_bits = self._bytes_to_bits(pattern_bytes)
        pattern_state = bits_to_state(pattern_bits, self.network.n)
        store_patterns_hebbian(self.network, [pattern_state], alpha=0.1)
        self.integrity_pattern = pattern_bytes

    def encrypt(self, plaintext):
        if self.integrity_pattern is not None:
            if len(plaintext) != 32:
                raise ValueError("Plaintext must be 32 bytes when integrity is enabled")
            data_to_encrypt = plaintext + self.integrity_pattern
        else:
            if len(plaintext) != 64:
                raise ValueError("Plaintext must be 64 bytes without integrity")
            data_to_encrypt = plaintext
        bits = self._bytes_to_bits(data_to_encrypt)
        left, right = bits[:256], bits[256:]
        for idx in range(self.rounds):
            f_out = self._round_function(right, idx)
            new_left = right.copy()
            new_right = self._xor_bits(left, f_out)
            left, right = new_left, new_right
        cipher_bits = np.concatenate([left, right])
        return self._bits_to_bytes(cipher_bits)

    def decrypt(self, ciphertext):
        if len(ciphertext) != self.block_size_bytes:
            raise ValueError(f"Ciphertext must be {self.block_size_bytes} bytes")
        bits = self._bytes_to_bits(ciphertext)
        left, right = bits[:256], bits[256:]
        for idx in reversed(range(self.rounds)):
            f_out = self._round_function(left, idx)
            new_right = left.copy()
            new_left = self._xor_bits(right, f_out)
            left, right = new_left, new_right
        plain_bits = np.concatenate([left, right])
        plain_bytes = self._bits_to_bytes(plain_bits)
        if self.integrity_pattern is not None:
            if plain_bytes[32:64] != self.integrity_pattern:
                raise ValueError("Integrity check failed: ciphertext tampered")
            return plain_bytes[:32]
        return plain_bytes

    def _round_function(self, half_bits, round_idx):
        state = bits_to_state(half_bits, self.network.n)
        state = self.network.evolve(self.steps_per_round, initial_state=state)
        return state_to_bits(state, 256)

    def _bytes_to_bits(self, data):
        bits = np.unpackbits(np.frombuffer(data, dtype=np.uint8))
        return bits.astype(np.uint8)

    def _bits_to_bytes(self, bits):
        return np.packbits(bits).tobytes()

    def _xor_bits(self, a, b):
        return np.bitwise_xor(a, b)