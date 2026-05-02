import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from network import ChaoticOscillatoryNetwork
from crypto import CAMCCipher
from dynamics import entropy, bit_flip_analysis, autocorrelation

st.set_page_config(page_title="Analysis", layout="wide")

st.title("Analysis")

N_NEURONS = 128
WEIGHT_SCALE = 2.0

with st.sidebar:
    st.header("Setup")
    seed = st.number_input("Seed", value=42, step=1)
    plaintext_len = st.slider("Plaintext length", 100, 2000, 500, 100)

@st.cache_resource
def setup(seed):
    rng = np.random.default_rng(seed)
    net = ChaoticOscillatoryNetwork(n_neurons=N_NEURONS, weight_scale=WEIGHT_SCALE)
    sync = np.exp(1j * rng.uniform(0, 2 * np.pi, N_NEURONS))
    return CAMCCipher(net, sync)

cipher = setup(seed)
plain = "A" * plaintext_len
ciphertext = cipher.encrypt(plain)

tab1, tab2, tab3 = st.tabs(["Entropy", "Avalanche", "Autocorrelation"])

with tab1:
    h = entropy(ciphertext)
    st.metric("Shannon entropy", f"{h:.4f} bits/byte", delta=f"{h-8:.4f} from ideal")

with tab2:
    av, std = bit_flip_analysis(cipher, "Test message.", trials=50)
    st.metric("Avalanche", f"{av*100:.1f}%", delta=f"±{std*100:.1f}%")
    st.caption("Fraction of ciphertext bits changed after flipping one plaintext bit. Ideal: 50%.")

with tab3:
    ac = autocorrelation(ciphertext, max_lag=30)
    fig, ax = plt.subplots(figsize=(8, 2))
    ax.stem(range(len(ac)), ac)
    ax.set_xlabel("Lag (bytes)")
    ax.set_ylabel("Correlation")
    st.pyplot(fig)