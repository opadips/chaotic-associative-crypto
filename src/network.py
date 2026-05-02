import numpy as np

class ChaoticOscillatoryNetwork:
    def __init__(self, n_neurons=128, weight_key=None, weight_scale=1.5):
        self.n = n_neurons
        self.weight_scale = weight_scale
        if weight_key is None:
            weight_key, weight_inv = self._generate_complex_weights()
            self.W = weight_key
            self.W_inv = weight_inv
        else:
            self.W = weight_key
            self.W_inv = self._compute_inverse(weight_key)
        self.b = np.zeros(self.n, dtype=complex)
        self.state = np.zeros(self.n, dtype=complex)

    def _generate_complex_weights(self):
        max_attempts = 10
        for _ in range(max_attempts):
            real = np.random.normal(0, self.weight_scale / np.sqrt(self.n), (self.n, self.n))
            imag = np.random.normal(0, self.weight_scale / np.sqrt(self.n), (self.n, self.n))
            W = (real + 1j * imag).astype(complex)
            cond = np.linalg.cond(W)
            if cond < 1e12:
                return W, np.linalg.inv(W)
        return W, np.linalg.inv(W)

    def _compute_inverse(self, W):
        return np.linalg.inv(W)

    def _tanhabs(self, z):
        magnitude = np.abs(z)
        angle = np.angle(z)
        return np.tanh(magnitude) * np.exp(1j * angle)

    def _arctanhabs(self, z):
        magnitude = np.abs(z)
        magnitude = np.clip(magnitude, None, 0.999999)
        angle = np.angle(z)
        return np.arctanh(magnitude) * np.exp(1j * angle)

    def step(self, state):
        linear = self.W @ state + self.b
        return self._tanhabs(linear)

    def inverse_step(self, state):
        linear = self._arctanhabs(state)
        return self.W_inv @ (linear - self.b)

    def evolve(self, steps, initial_state=None):
        if initial_state is not None:
            self.state = initial_state.copy()
        for _ in range(steps):
            self.state = self.step(self.state)
        return self.state.copy()

    def evolve_inverse(self, steps, state):
        current = state.copy()
        for _ in range(steps):
            current = self.inverse_step(current)
        return current

    def set_state(self, state):
        self.state = state.copy()

    def get_state(self):
        return self.state.copy()