import streamlit as st
import numpy as np
from network import ChaoticOscillatoryNetwork
from block_cipher import CAMCBlockCipher

st.title("Encrypt / Decrypt")

N = 128
SCALE = 1.5
ROUNDS = 8
STEPS = 2

@st.cache_resource
def build_cipher(seed):
    rng = np.random.default_rng(seed)
    net = ChaoticOscillatoryNetwork(n_neurons=N, weight_scale=SCALE)
    return CAMCBlockCipher(net, rounds=ROUNDS, steps_per_round=STEPS)

seed = st.sidebar.number_input("Seed", value=42)
mode = st.sidebar.selectbox("Mode", ["64-byte block", "32-byte + integrity"])

st.sidebar.markdown("---")
st.sidebar.caption("Encryption and decryption use the same seed and mode.")

cipher = build_cipher(seed)

tab1, tab2 = st.tabs(["Encrypt", "Decrypt"])

with tab1:
    st.subheader("Plaintext → Ciphertext")
    if mode == "32-byte + integrity":
        pattern_str = st.text_input("Integrity pattern (32 bytes)", "CHKSUM1234CHECKSABCDEFGHIJKLMNOP", key="pat_enc")
        plaintext = st.text_area("Plaintext (max 32 bytes)", "A"*32, max_chars=32, key="pt_enc")
    else:
        pattern_str = None
        plaintext = st.text_area("Plaintext (max 64 bytes)", "A"*64, max_chars=64, key="pt_enc64")

    if st.button("Encrypt", use_container_width=True):
        if mode == "32-byte + integrity":
            if len(pattern_str) != 32:
                st.error("Integrity pattern must be exactly 32 bytes.")
            else:
                pt = plaintext.encode().ljust(32)[:32]
                pat = pattern_str.encode()[:32]
                full = pt + pat
                ct = cipher.encrypt(full)
                st.session_state.last_ct = ct.hex()
                st.text_area("Ciphertext", ct.hex(), height=100)
        else:
            pt = plaintext.encode().ljust(64)[:64]
            ct = cipher.encrypt(pt)
            st.session_state.last_ct = ct.hex()
            st.text_area("Ciphertext", ct.hex(), height=100)

with tab2:
    st.subheader("Ciphertext → Plaintext")
    ct_hex = st.text_area("Ciphertext (hex)", value=st.session_state.get("last_ct", ""), key="ct_input", height=100)
    if mode == "32-byte + integrity":
        pattern_str = st.text_input("Integrity pattern (32 bytes)", "CHKSUM1234CHECKSABCDEFGHIJKLMNOP", key="pat_dec")
    else:
        pattern_str = None

    if st.button("Decrypt", use_container_width=True):
        try:
            ct = bytes.fromhex(ct_hex.strip())
            if len(ct) != 64:
                st.error("Ciphertext must be exactly 64 bytes (128 hex chars).")
            else:
                pt = cipher.decrypt(ct)
                if mode == "32-byte + integrity":
                    msg = pt[:32]
                    pat = pt[32:]
                    if pattern_str and pat == pattern_str.encode()[:32]:
                        st.success("Integrity check passed.")
                        st.text_area("Decrypted message", msg.decode(errors='replace'), height=100)
                    else:
                        st.error("Integrity check FAILED – ciphertext tampered or wrong key/pattern.")
                else:
                    st.text_area("Decrypted", pt.decode(errors='replace'), height=100)
        except ValueError as e:
            st.error(f"Decryption error: {e}")
        except Exception as e:
            st.error(f"Invalid hex string: {e}")