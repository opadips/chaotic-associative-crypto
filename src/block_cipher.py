import numpy as np
from network import ChaoticOscillatoryNetwork
from encoding import bits_to_state, state_to_bits

class CAMCBlockCipher:
    def __init__(self, network, rounds=12, steps_per_round=1):
        self.network = network
        self.rounds = rounds
        self.steps_per_round = steps_per_round
        self.block_size_bytes = 64
        self.block_size_bits = self.block_size_bytes * 8

    def encrypt(self, plaintext):
        if len(plaintext) != self.block_size_bytes:
            raise ValueError(f"Plaintext must be {self.block_size_bytes} bytes")
        bits = self._bytes_to_bits(plaintext)
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
        return self._bits_to_bytes(plain_bits)

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