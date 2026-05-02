import streamlit as st

st.set_page_config(page_title="Design", layout="wide")

st.title("Design & Constraints")

st.header("What this is")
st.markdown(
"""
CAMC is a proof-of-concept stream cipher built on a chaotic oscillatory
neural network with associative memory. It tests whether complex dynamics
can yield keystreams with high entropy and low predictability.
"""
)

st.header("What this is not")
st.markdown(
"""
- Not a production-ready cipher.
- Not faster than AES.
- Not formally proven secure.
"""
)

st.header("Known limitations")
st.markdown(
"""
- **Speed**: 500–1000× slower than AES for equivalent security margin.
- **Sync requirement**: Both sides must share identical weight key and sync state.
- **No standardisation**: No NIST or ISO review.
- **Tamper detection**: The associative memory provides implicit integrity check,
  but no cryptographic MAC guarantees.
"""
)

st.header("Architecture")
st.code("""
Plaintext ──► encode ──► ChaoticOscillatoryNetwork
                              │ (weight matrix = key)
                              ▼
                        keystream bytes
                              │
                              ▼
                     XOR ◄── Ciphertext
""")