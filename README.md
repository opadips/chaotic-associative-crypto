# CAMC: Chaotic Associative Memory Cryptography

**Proof-of-concept block cipher.** Uses a Feistel network where the
round function is a chaotic oscillatory recurrent neural network with
associative memory. A 64-byte block cipher with optional 32-byte
integrity pattern. Implicit tamper detection from the network's
attractor dynamics.

**Not for production.** No formal security review. Far slower than
standard ciphers.

## Quick start

Requires Python 3.10 or later.

```bash
git clone https://github.com/opadips/chaotic-associative-crypto.git
cd chaotic-associative-crypto
pip install -e .
```

```python
from network import ChaoticOscillatoryNetwork
from block_cipher import CAMCBlockCipher
import numpy as np

net = ChaoticOscillatoryNetwork(n_neurons=128, weight_scale=1.5)
cipher = CAMCBlockCipher(net, rounds=12, steps_per_round=3)

plaintext = b"A" * 64
ciphertext = cipher.encrypt(plaintext)
decrypted = cipher.decrypt(ciphertext)
assert decrypted == plaintext
```

Streamlit demo:

```bash
cd app
streamlit run streamlit_app.py
```

## Architecture

Core: `N` complex-valued neurons, each with magnitude and phase.
State update:

```
z(t+1) = f(W @ z(t) + b)
```

- **W**: complex weight matrix (the secret key). Generated from a
  Gaussian distribution scaled by `weight_scale / sqrt(N)`.
- **f**: activation. Default `modular` (keeps phase, normalises
  magnitude to 1).
- **Associative memory**: Hebbian patterns can be stored in W,
  creating attractors.

### Cipher construction

64-byte Feistel network (12 rounds, 3 network steps per round).
Round function `F(R, round_idx)`:
1. Expands 32-byte half-block to 128 bytes (tiling).
2. Maps bytes to initial phases of all 128 neurons (magnitude 0.5).
3. Evolves network for `steps_per_round` iterations.
4. Passes final 128 neuron phases through a 32-bit mixing accumulator
   (XOR, shifts) to produce 32 pseudorandom bytes.

Feistel guarantees invertibility. The mixing accumulator provides
diffusion from all 128 neurons.

### Integrity mode

A 32-byte integrity pattern is appended to the plaintext before
encryption (total 64 bytes). After decryption, the pattern field
is compared byte-for-byte. Tampering with the ciphertext causes
the chaotic decryption to diverge and produce a wrong pattern;
`decrypt` raises `ValueError`.

## Measured properties

N=128, 12 rounds, 3 steps/round, 64-byte blocks:

| Property | Result |
|----------|--------|
| Encrypt/decrypt roundtrip | passes |
| Avalanche effect | ~50% |
| Autocorrelation (lag 1) | <0.1 |
| Integrity tamper detection | 100% reliable in tests |
| Shannon entropy | ~5.7 bits/byte (see Limitations) |

## Limitations

- **Entropy**: The round function output has residual correlation.
  Entropy ~5.7 bits/byte, below the ideal 8. This can be improved
  with more rounds, stronger mixing, or using `tanhabs` activation.
  Kept as-is to demonstrate the underlying dynamics transparently.
- **Speed**: ~2000x slower than AES at comparable block size.
- **Key size**: N=128 requires 128x128 complex numbers. Not practical
  without structured key expansion (not implemented).
- **No formal security reduction**: Security relies on difficulty of
  predicting chaotic trajectories.
- **Fixed block size**: 64 bytes only. No chaining mode for longer
  messages.

## Project structure

```
src/
  network.py        # ChaoticOscillatoryNetwork
  associative.py    # Hebbian pattern storage
  dynamics.py       # Lyapunov exponent, entropy, etc.
  block_cipher.py   # CAMCBlockCipher (Feistel)
  encoding.py       # bits <-> complex state
tests/
  test_block_cipher.py  # roundtrip, avalanche, integrity
  test_dynamics.py      # chaos metrics
notebooks/
  03_security_analysis.ipynb
  04_butterfly_effect.ipynb
app/
  streamlit_app.py
  page_encrypt.py
  page_analysis.py
  page_about.py
```

## License

MIT. See `LICENSE`.
