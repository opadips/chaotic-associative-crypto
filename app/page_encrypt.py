import streamlit as st
import numpy as np
from network import ChaoticOscillatoryNetwork
from crypto import CAMCCipher

st.title("Encrypt / Decrypt")

N_NEURONS = 128
WEIGHT_SCALE = 2.0

@st.cache_resource
def get_network_and_cipher(seed, sync_seed):
    rng = np.random.default_rng(seed)
    net = ChaoticOscillatoryNetwork(n_neurons=N_NEURONS, weight_scale=WEIGHT_SCALE)
    sync_state = np.exp(1j * rng.uniform(0, 2 * np.pi, N_NEURONS))
    cipher = CAMCCipher(net, sync_state)
    return net, cipher, sync_state

col1, col2 = st.columns([1, 2], gap="large")

with col1:
    st.header("Parameters")
    weight_seed = st.number_input("Weight seed", value=42, min_value=0, step=1)
    sync_seed = st.number_input("Sync seed", value=123, min_value=0, step=1)
    plaintext = st.text_area("Plaintext", value="Hello, CAMC.")

    enc_btn = st.button("Encrypt", use_container_width=True)
    dec_btn = st.button("Decrypt", use_container_width=True)

with col2:
    if enc_btn or dec_btn:
        _, cipher, _ = get_network_and_cipher(weight_seed, sync_seed)

        if enc_btn:
            ciphertext = cipher.encrypt(plaintext)
            st.session_state['ciphertext'] = ciphertext
            st.text_area("Ciphertext (hex)", value=ciphertext.hex(), height=100)

        if dec_btn and 'ciphertext' in st.session_state:
            decrypted = cipher.decrypt(st.session_state['ciphertext'])
            st.text_area("Decrypted", value=decrypted, height=100)