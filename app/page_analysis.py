import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from network import ChaoticOscillatoryNetwork
from block_cipher import CAMCBlockCipher
from dynamics import entropy, autocorrelation

st.title("Analysis")

N = 128
SCALE = 1.5
ROUNDS = 8
STEPS = 2

with st.sidebar:
    st.header("Setup")
    seed = st.number_input("Seed", value=42, step=1)

@st.cache_resource
def get_cipher(seed):
    rng = np.random.default_rng(seed)
    net = ChaoticOscillatoryNetwork(n_neurons=N, weight_scale=SCALE)
    return CAMCBlockCipher(net, rounds=ROUNDS, steps_per_round=STEPS)

cipher = get_cipher(seed)
plain = b"A" * 64
ct = cipher.encrypt(plain)

tab1, tab2, tab3 = st.tabs(["Entropy", "Avalanche", "Autocorrelation"])

with tab1:
    h = entropy(ct)
    st.metric("Shannon entropy", f"{h:.4f} bits/byte", delta=f"{h-8:.4f} from ideal")

with tab2:
    p2 = bytearray(plain)
    p2[0] ^= 0x01
    c2 = cipher.encrypt(bytes(p2))
    diff = sum(bin(a ^ b).count('1') for a, b in zip(ct, c2))
    ratio = diff / (len(ct) * 8)
    st.metric("Avalanche", f"{ratio*100:.1f}%", delta="Ideal: 50%")

with tab3:
    ac = autocorrelation(ct, max_lag=30)
    fig, ax = plt.subplots(figsize=(8, 2))
    ax.stem(range(len(ac)), ac)
    ax.set_xlabel("Lag (bytes)")
    ax.set_ylabel("Correlation")
    st.pyplot(fig)