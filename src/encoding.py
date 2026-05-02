import numpy as np

def bits_to_state(bits, n_neurons):
    state = np.zeros(n_neurons, dtype=complex)
    bits_per_neuron = 8
    for i in range(n_neurons):
        start = i * bits_per_neuron
        if start + bits_per_neuron > len(bits):
            break
        byte_val = 0
        for j in range(bits_per_neuron):
            if bits[start + j]:
                byte_val |= (1 << j)
        angle = (byte_val / 256.0) * 2 * np.pi
        state[i] = np.exp(1j * angle) * 0.5
    return state

def state_to_bits(state, num_bits):
    bits = np.zeros(num_bits, dtype=np.uint8)
    bits_per_neuron = 8
    for i in range(min(len(state), num_bits // bits_per_neuron)):
        angle = np.angle(state[i])
        angle = np.mod(angle, 2 * np.pi)
        byte_val = int(round(angle / (2 * np.pi) * 255)) % 256
        for j in range(bits_per_neuron):
            if byte_val & (1 << j):
                bits[i * bits_per_neuron + j] = 1
    return bits