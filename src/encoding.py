import numpy as np

def text_to_initial_state(text, n_neurons):
    data = text.encode('utf-8')
    if len(data) > n_neurons * 4:
        raise ValueError(f"text too long: {len(data)} bytes, max {n_neurons * 4}")
    padded = data.ljust(n_neurons * 4, b'\x00')
    phases = []
    for i in range(n_neurons):
        chunk = padded[i*4:(i+1)*4]
        val = int.from_bytes(chunk, 'big')
        angle = (val / (2**32)) * 2 * np.pi
        phases.append(angle)
    return np.exp(1j * np.array(phases))

def initial_state_to_text(state):
    phases = np.angle(state)
    phases = np.mod(phases, 2 * np.pi)
    data = bytearray()
    for angle in phases:
        val = int((angle / (2 * np.pi)) * (2**32))
        if val >= 2**32:
            val = 2**32 - 1
        data.extend(val.to_bytes(4, 'big'))
    first_null = data.find(b'\x00\x00\x00\x00')
    if first_null != -1:
        data = data[:first_null]
    return bytes(data).decode('utf-8', errors='replace')