import streamlit as st
import numpy as np
from network import ChaoticOscillatoryNetwork
from block_cipher import CAMCBlockCipher

st.title("Encrypt / Decrypt")

N_NEURONS = 128
WEIGHT_SCALE = 1.5
ROUNDS = 8
STEPS = 2

@st.cache_resource
def get_cipher(seed):
    rng = np.random.default_rng(seed)
    net = ChaoticOscillatoryNetwork(n_neurons=N_NEURONS, weight_scale=WEIGHT_SCALE)
    cipher = CAMCBlockCipher(net, rounds=ROUNDS, steps_per_round=STEPS)
    return cipher

col1, col2 = st.columns([1, 2], gap="large")

with col1:
    st.header("Parameters")
    seed = st.number_input("Weight seed", value=42, min_value=0, step=1)
    mode = st.radio("Mode", ["64-byte block (no integrity)", "32-byte + integrity pattern"])

    if mode == "32-byte + integrity pattern":
        pattern_str = st.text_input("Integrity pattern (32 chars)", value="CHKSUM1234CHECKSABCDEFGHIJKLMNOP")
        plaintext = st.text_area("Plaintext (32 bytes)", value="A" * 32, max_chars=32)
    else:
        plaintext = st.text_area("Plaintext (64 bytes)", value="A" * 64, max_chars=64)

    enc_btn = st.button("Encrypt", use_container_width=True)
    dec_btn = st.button("Decrypt", use_container_width=True)

with col2:
    cipher = get_cipher(seed)

    if enc_btn:
        if mode == "32-byte + integrity pattern":
            if len(pattern_str) != 32:
                st.error("Integrity pattern must be exactly 32 characters.")
            else:
                cipher.set_integrity_pattern(pattern_str.encode())
                pt_bytes = plaintext.encode().ljust(32)[:32]
                ct = cipher.encrypt(pt_bytes)
                st.session_state['ciphertext'] = ct
                st.session_state['mode'] = 'integrity'
                st.text_area("Ciphertext (hex)", value=ct.hex(), height=100)
        else:
            pt_bytes = plaintext.encode().ljust(64)[:64]
            ct = cipher.encrypt(pt_bytes)
            st.session_state['ciphertext'] = ct
            st.session_state['mode'] = 'block'
            st.text_area("Ciphertext (hex)", value=ct.hex(), height=100)

    if dec_btn and 'ciphertext' in st.session_state:
        try:
            if st.session_state.get('mode') == 'integrity' and pattern_str:
                cipher.set_integrity_pattern(pattern_str.encode())
            pt = cipher.decrypt(st.session_state['ciphertext'])
            st.text_area("Decrypted", value=pt.decode(errors='replace'), height=100)
        except ValueError as e:
            st.error(str(e))