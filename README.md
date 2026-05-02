# CAMC: Chaotic Associative Memory Cryptography

**Proof-of-concept stream cipher.** Uses a complex-valued oscillatory recurrent neural network with associative memory to generate keystreams. The network's chaos and attractor dynamics provide high entropy and implicit tamper detection.

**Not for production.** This is a research artifact. It has not undergone formal cryptographic review. It is orders of magnitude slower than standard ciphers.

## Installation

Requires Python 3.10 or newer.

```bash
git clone https://github.com/YOUR_USERNAME/chaotic-associative-crypto.git
cd chaotic-associative-crypto
pip install -e .
```

## Quick Start

```python
from network import ChaoticOscillatoryNetwork
from crypto import CAMCCipher
import numpy as np

n_neurons = 128
weight_scale = 2.0
seed = 42

rng = np.random.default_rng(seed)
network = ChaoticOscillatoryNetwork(n_neurons=n_neurons, weight_scale=weight_scale)
sync_state = np.exp(1j * rng.uniform(0, 2 * np.pi, n_neurons))

cipher = CAMCCipher(network, sync_state)
plaintext = "Secret message."
ciphertext = cipher.encrypt(plaintext)
decrypted = cipher.decrypt(ciphertext)

print(f"Ciphertext (hex): {ciphertext.hex()}")
print(f"Decrypted: {decrypted}")
```

## Streamlit Demo

```bash
cd app
streamlit run streamlit_app.py
```

Three pages: Encrypt (interactive encryption/decryption), Analysis (entropy, avalanche, autocorrelation), Design (architecture and limitations).

## Architecture

The core is a network of `n` complex-valued neurons. Each neuron's state evolves according to:

```
z(t+1) = f(W · z(t) + b)
```

- **W**: complex weight matrix (the secret key). Generated from a Gaussian distribution scaled by `weight_scale/√n`.
- **f**: activation function, typically `modular` – preserves phase, normalises magnitude to 1 (states stay on the unit circle).
- **Associative memory**: Hebbian patterns can be stored in W, creating attractors that the network falls into if the input is sufficiently close. In this cipher, it provides implicit integrity: tampering with ciphertext disrupts synchronisation, pushing the receiver's network into a wrong attractor, causing decryption to produce garbage.

### Keystream Generation

The network is seeded with a synchronisation state `sync_state` (derived from a shared secret). For each required keystream byte:

1. Advance the network by one step (or multiple mixing steps).
2. Extract the phase of every neuron.
3. For each phase, compute a byte value, then accumulate it into a 32-bit mixer using XOR and bidirectional shifts.
4. Emit the low byte of the accumulator as a keystream byte.

This per-neuron accumulation guarantees that even with modular activation (all magnitudes equal), the output distribution is uniform.

Encryption/Decryption is bytewise XOR of plaintext/ciphertext with the keystream.

## Security Properties

Measured with `N=128`, `weight_scale=2.0`, plaintext length 500–1000 bytes.

| Metric | Value | Ideal |
|--------|-------|-------|
| Shannon entropy | >7.9 bits/byte | 8.0 |
| Avalanche effect | ~50% | 50% |
| Autocorrelation (lag 1) | <0.1 | 0.0 |
| Largest Lyapunov exponent | >0.5 | positive |

All tests reproducible via:

```bash
pytest tests/ -v
```

Jupyter notebooks `notebooks/03_security_analysis.ipynb` and `notebooks/04_butterfly_effect.ipynb` contain detailed plots and analysis.

## Limitations

- **Performance**: The chaotic network requires many floating-point operations per byte. At `N=128`, encryption is ~500× slower than AES.
- **Synchronisation**: Both parties must hold the **exact** weight matrix and sync state. Any difference (bit flip) causes immediate desynchronisation and decryption failure. This is a feature for integrity but a challenge for key distribution.
- **No formal security reduction**: Security relies on the difficulty of predicting chaotic trajectories and solving the inverse initial value problem. No reduction to a known hard mathematical problem exists yet.
- **No authenticated encryption**: While the associative memory provides some implicit integrity, there is no proper MAC. Active attacks may craft valid-looking ciphertexts under different keys.
- **Key size**: The key (weight matrix) is `n²` complex numbers. For `n=128`, that is 16,384 complex values; too large for practical key exchange without compression or structured generation (not implemented here).

## Project Structure

```
src/
  network.py         # ChaoticOscillatoryNetwork class
  associative.py      # Hebbian pattern storage and recall
  dynamics.py         # Lyapunov exponent, divergence, statistical tools
  crypto.py           # CAMCCipher stream cipher
  encoding.py         # Text ↔ complex state mapping
tests/
  test_crypto.py      # Encrypt/decrypt, wrong sync, avalanche
  test_dynamics.py    # Chaos metrics and ciphertext statistics
notebooks/
  03_security_analysis.ipynb
  04_butterfly_effect.ipynb
app/
  streamlit_app.py    # Main entry point
  page_encrypt.py
  page_analysis.py
  page_about.py
```

## Contributing

Bug reports and pull requests are welcome. This is an exploratory research project; contributions that add new analysis, visualisations, or attack descriptions are especially valued.

## License

MIT. See `LICENSE` file.