import streamlit as st

st.title("Design & Constraints")

st.header("Architecture")
st.markdown(
"""
**CAMC Block Cipher** — a 64-byte block cipher built on a Feistel network.
The round function is a chaotic oscillatory neural network with 128 complex
neurons and modular activation. Each round applies the network to half the
block, evolving it for a fixed number of steps, then XORs the result with
the other half.
"""
)

st.code("""
Left (32B)    Right (32B)
    |              |
    v              v
[Chaotic RNN] -> XOR -> swap
    |              |
    v              v
  repeat 8 rounds
""")

st.header("Integrity Mode")
st.markdown(
"""
When an integrity pattern (32 bytes) is set, the cipher encrypts a 32-byte
message appended with the pattern to form a 64-byte block. On decryption,
the pattern field is compared byte-for-byte with the original. Any mismatch
— caused by tampering — raises a `ValueError`. The associative memory
stored in the network's weights contributes to error amplification.
"""
)

st.header("Limitations")
st.markdown(
"""
- **Performance**: 8 rounds * 2 network steps per round = 16 full network
  evolutions per block. At N=128, this is ~2000× slower than AES.
- **Key size**: The weight matrix requires `128×128` complex numbers.
  Not practical without structured key expansion (not implemented).
- **No formal security reduction**: Security relies on the chaotic
  dynamics of the round function, not a proven hard problem.
- **Fixed block size**: Only 64-byte blocks. No mode of operation
  for longer messages (CBC, CTR not implemented).
"""
)