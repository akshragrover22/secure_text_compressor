import heapq
from collections import Counter, namedtuple
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad

# --- Huffman Compression ---

class Node(namedtuple("Node", "char freq left right")):
    def __lt__(self, other): return self.freq < other.freq

def build_huffman_tree(text):
    freq = Counter(text)
    heap = [Node(c, f, None, None) for c, f in freq.items()]
    heapq.heapify(heap)

    while len(heap) > 1:
        a = heapq.heappop(heap)
        b = heapq.heappop(heap)
        merged = Node(None, a.freq + b.freq, a, b)
        heapq.heappush(heap, merged)

    return heap[0]

def generate_codes(node, prefix='', code_map=None):
    if code_map is None:
        code_map = {}
    if node:
        if node.char:
            code_map[node.char] = prefix
        generate_codes(node.left, prefix + '0', code_map)
        generate_codes(node.right, prefix + '1', code_map)
    return code_map

def compress(text):
    tree = build_huffman_tree(text)
    code_map = generate_codes(tree)
    binary_string = ''.join(code_map[c] for c in text)
    return binary_string, tree

def bin_string_to_bytes(binary_string):
    return int(binary_string, 2).to_bytes((len(binary_string) + 7) // 8, byteorder='big')

# --- AES Encryption ---

def encrypt(data_bytes, key):
    cipher = AES.new(key, AES.MODE_CBC)
    ct_bytes = cipher.encrypt(pad(data_bytes, AES.block_size))
    return cipher.iv + ct_bytes

def decrypt(encrypted_data, key):
    iv = encrypted_data[:16]
    ct = encrypted_data[16:]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return unpad(cipher.decrypt(ct), AES.block_size)

def decompress(binary_string, tree):
    result = []
    node = tree
    for bit in binary_string:
        if bit == '0':
            node = node.left
        else:
            node = node.right
        if node.char is not None:
            result.append(node.char)
            node = tree
    return ''.join(result)

def decrypt_and_decompress(encrypted_data, key, tree):
    decrypted_bytes = decrypt(encrypted_data, key)
    binary_string = bin(int.from_bytes(decrypted_bytes, byteorder='big'))[2:]
    
    # Pad binary string to original length
    # You MUST store the original length to trim correctly
    return binary_string

# Global storage (simulate temporary memory)
global_saved = {}

# --- Main Program ---

def main():
    key = b'thisis16bytekey!'  # 16 bytes AES key

    while True:
        print("\n🔐 Secure Data Compressor")
        print("1. Compress and Encrypt Text")
        print("2. Decrypt and Decompress Text")
        print("3. Exit")

        choice = input("Enter your choice: ")

        if choice == '1':
            text = input("\n🔹 Enter text to compress and encrypt:\n")
            binary_data, tree = compress(text)
            data_bytes = bin_string_to_bytes(binary_data)
            encrypted = encrypt(data_bytes, key)

            print(f"\n📦 Compressed binary length: {len(binary_data)} bits")
            print(f"🔒 Encrypted (hex): {encrypted.hex()}")

            # Save for later
            global_saved["encrypted"] = encrypted
            global_saved["tree"] = tree
            global_saved["length"] = len(binary_data)

        elif choice == '2':
            if "encrypted" not in global_saved:
                print("⚠️ No encrypted data found. Run option 1 first.")
                continue

            encrypted = global_saved["encrypted"]
            tree = global_saved["tree"]
            original_len = global_saved["length"]

            decrypted_bytes = decrypt(encrypted, key)
            binary_str = bin(int.from_bytes(decrypted_bytes, byteorder='big'))[2:]

            while len(binary_str) < original_len:
                binary_str = '0' + binary_str

            original_text = decompress(binary_str, tree)
            print(f"\n✅ Decrypted and decompressed text:\n{original_text}")

        elif choice == '3':
            print("👋 Exiting. Goodbye!")
            break

        else:
            print("❌ Invalid choice. Try again.")

if __name__ == "__main__":
    main()
