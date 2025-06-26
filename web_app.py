import streamlit as st
from compressor import compress, decompress, encrypt, decrypt, bin_string_to_bytes

key = b'thisis16bytekey!'

st.title("🔐 Secure Text Compressor (Huffman + AES)")

text_input = st.text_area("Enter text to compress & encrypt")

if st.button("Compress & Encrypt"):
    if text_input:
        binary, tree = compress(text_input)
        data_bytes = bin_string_to_bytes(binary)
        encrypted = encrypt(data_bytes, key)

        st.success("✅ Encrypted!")
        st.code(encrypted.hex(), language='text')

        st.session_state["encrypted"] = encrypted
        st.session_state["tree"] = tree
        st.session_state["length"] = len(binary)

if st.button("Decrypt & Decompress"):
    if "encrypted" in st.session_state:
        decrypted_bytes = decrypt(st.session_state["encrypted"], key)
        binary_str = bin(int.from_bytes(decrypted_bytes, byteorder='big'))[2:]

        while len(binary_str) < st.session_state["length"]:
            binary_str = '0' + binary_str

        text = decompress(binary_str, st.session_state["tree"])
        st.success("✅ Original text:")
        st.code(text, language='text')
    else:
        st.warning("⚠️ First encrypt some text!")
