import numpy as np
from encoding import text_to_initial_state, initial_state_to_text

class CAMCCipher:
    def __init__(self, network, sync_state):
        self.network = network
        self.sync_state = np.asarray(sync_state, dtype=complex)
        self.block_size = 4

    def encrypt(self, plaintext):
        self.network.set_state(self.sync_state.copy())
        data = plaintext.encode('utf-8')
        keystream = self._generate_keystream(len(data))
        encrypted = bytes(b ^ k for b, k in zip(data, keystream))
        return encrypted

    def decrypt(self, ciphertext):
        self.network.set_state(self.sync_state.copy())
        keystream = self._generate_keystream(len(ciphertext))
        decrypted = bytes(c ^ k for c, k in zip(ciphertext, keystream))
        return decrypted.decode('utf-8', errors='replace')

    def _generate_keystream(self, length):
        stream = bytearray()
        while len(stream) < length:
            self.network.step(self.network.state)
            raw = bytearray()
            for val in self.network.state[:self.block_size]:
                angle = np.angle(val)
                normalized = int((np.mod(angle, 2 * np.pi) / (2 * np.pi)) * 256) % 256
                raw.append(normalized)
            stream.extend(raw)
        return bytes(stream[:length])