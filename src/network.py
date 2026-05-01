import numpy as np

class ChaoticOscillatoryNetwork:
    def __init__(self, n_neurons=128, weight_key=None, activation='tanhabs'):
        self.n = n_neurons
        if weight_key is None:
            weight_key = self._generate_complex_weights()
        self.W = weight_key
        self.b = np.zeros(self.n, dtype=complex)
        self.state = np.zeros(self.n, dtype=complex)
        if activation == 'tanhabs':
            self._activation = self._tanhabs
        elif activation == 'modular':
            self._activation = self._modular
        else:
            raise ValueError(f"Unsupported activation: {activation}")

    def _generate_complex_weights(self):
        real = np.random.normal(0, 1 / np.sqrt(self.n), (self.n, self.n))
        imag = np.random.normal(0, 1 / np.sqrt(self.n), (self.n, self.n))
        return (real + 1j * imag).astype(complex)

    def _tanhabs(self, z):
        magnitude = np.abs(z)
        angle = np.angle(z)
        return np.tanh(magnitude) * np.exp(1j * angle)

    def _modular(self, z):
        return np.exp(1j * np.angle(z))

    def step(self, state):
        linear = self.W @ state + self.b
        return self._activation(linear)

    def evolve(self, steps, initial_state=None, record=False):
        if initial_state is not None:
            self.state = initial_state.copy()
        if record:
            history = np.zeros((steps + 1, self.n), dtype=complex)
            history[0] = self.state.copy()
            for t in range(steps):
                self.state = self.step(self.state)
                history[t + 1] = self.state.copy()
            return history
        for _ in range(steps):
            self.state = self.step(self.state)
        return self.state.copy()

    def set_state(self, state):
        self.state = state.copy()

    def get_state(self):
        return self.state.copy()