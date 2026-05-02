import numpy as np
from encoding import text_to_initial_state, initial_state_to_text

class CAMCCipher:
    def __init__(self, network, sync_state):
        self.network = network
        self.sync_state = np.asarray(sync_state, dtype=complex)
        self.accumulator = 0xDEADBEEF

    def encrypt(self, plaintext):
        self.network.set_state(self.sync_state.copy())
        self.accumulator = 0xDEADBEEF
        data = plaintext.encode('utf-8')
        keystream = self._generate_keystream(len(data))
        encrypted = bytes(b ^ k for b, k in zip(data, keystream))
        return encrypted

    def decrypt(self, ciphertext):
        self.network.set_state(self.sync_state.copy())
        self.accumulator = 0xDEADBEEF
        keystream = self._generate_keystream(len(ciphertext))
        decrypted = bytes(c ^ k for c, k in zip(ciphertext, keystream))
        return decrypted.decode('utf-8', errors='replace')

    def _generate_keystream(self, length):
        stream = bytearray()
        n = self.network.n
        while len(stream) < length:
            self.network.step(self.network.state)
            angles = np.mod(np.angle(self.network.state), 2 * np.pi)
            for angle in angles:
                byte_val = int((angle / (2 * np.pi)) * 256) & 0xFF
                self.accumulator ^= byte_val
                self.accumulator ^= (self.accumulator >> 7)
                self.accumulator ^= (self.accumulator << 9)
                self.accumulator &= 0xFFFFFFFF
                stream.append(self.accumulator & 0xFF)
                if len(stream) >= length:
                    return bytes(stream)
        return bytes(stream)