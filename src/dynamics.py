import numpy as np

def lyapunov_exponent(network, initial_state, steps=1000, delta=1e-8):
    n = network.n
    state = np.asarray(initial_state, dtype=complex).copy()
    perturbation = np.random.normal(0, delta, n) + 1j * np.random.normal(0, delta, n)
    perturbed_state = state + perturbation
    total_divergence = 0.0
    for _ in range(steps):
        state = network.step(state)
        perturbed_state = network.step(perturbed_state)
        diff = perturbed_state - state
        distance = np.sqrt(np.sum(np.abs(diff) ** 2))
        if distance < 1e-15:
            distance = 1e-15
        total_divergence += np.log(distance / delta)
        perturbed_state = state + (diff / distance) * delta
    return total_divergence / steps

def divergence_curve(network, initial_state_a, initial_state_b, steps):
    state_a = np.asarray(initial_state_a, dtype=complex).copy()
    state_b = np.asarray(initial_state_b, dtype=complex).copy()
    distances = np.zeros(steps + 1)
    distances[0] = np.sqrt(np.sum(np.abs(state_b - state_a) ** 2))
    for t in range(steps):
        state_a = network.step(state_a)
        state_b = network.step(state_b)
        distances[t + 1] = np.sqrt(np.sum(np.abs(state_b - state_a) ** 2))
    return distances

def bit_flip_analysis(cipher_instance, plaintext, trials=100):
    base_encrypted = cipher_instance.encrypt(plaintext)
    data = plaintext.encode('utf-8')
    total_bits = len(data) * 8
    flipped_counts = []
    for _ in range(trials):
        byte_idx = np.random.randint(0, len(data))
        bit_idx = np.random.randint(0, 8)
        modified = bytearray(data)
        modified[byte_idx] ^= (1 << bit_idx)
        modified_plain = bytes(modified).decode('utf-8', errors='replace')
        modified_encrypted = cipher_instance.encrypt(modified_plain)
        diff_bits = sum(
            bin(a ^ b).count('1')
            for a, b in zip(base_encrypted, modified_encrypted)
        )
        flipped_counts.append(diff_bits / max(len(base_encrypted) * 8, 1))
    return np.mean(flipped_counts), np.std(flipped_counts)

def ciphertext_histogram(cipher_instance, plaintext):
    encrypted = cipher_instance.encrypt(plaintext)
    values = np.frombuffer(encrypted, dtype=np.uint8)
    hist, _ = np.histogram(values, bins=256, range=(0, 255))
    return hist

def entropy(data):
    values = np.frombuffer(data, dtype=np.uint8)
    _, counts = np.unique(values, return_counts=True)
    probs = counts / len(values)
    return -np.sum(probs * np.log2(probs + 1e-15))

def autocorrelation(data, max_lag=100):
    values = np.frombuffer(data, dtype=np.uint8).astype(float)
    mean = np.mean(values)
    variance = np.var(values)
    if variance < 1e-10:
        return np.ones(max_lag + 1)
    result = np.zeros(max_lag + 1)
    for lag in range(max_lag + 1):
        if len(values) - lag <= 0:
            break
        result[lag] = np.mean((values[:len(values)-lag] - mean) * (values[lag:] - mean)) / variance
    return result