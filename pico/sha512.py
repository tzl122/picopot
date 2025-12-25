import struct

def _rotr(x, n):
    return ((x >> n) | (x << (64 - n))) & 0xffffffffffffffff

def _sha512_compress(chunk, h):
    w = [0] * 80
    w[0:16] = struct.unpack(">16Q", chunk)

    for i in range(16, 80):
        s0 = _rotr(w[i - 15], 1) ^ _rotr(w[i - 15], 8) ^ (w[i - 15] >> 7)
        s1 = _rotr(w[i - 2], 19) ^ _rotr(w[i - 2], 61) ^ (w[i - 2] >> 6)
        w[i] = (w[i - 16] + s0 + w[i - 7] + s1) & 0xffffffffffffffff

    a, b, c, d, e, f, g, hh = h

    K = [
        0x428a2f98d728ae22, 0x7137449123ef65cd,
        0xb5c0fbcfec4d3b2f, 0xe9b5dba58189dbbc,
        0x3956c25bf348b538, 0x59f111f1b605d019,
        0x923f82a4af194f9b, 0xab1c5ed5da6d8118,
        0xd807aa98a3030242, 0x12835b0145706fbe,
        0x243185be4ee4b28c, 0x550c7dc3d5ffb4e2,
        0x72be5d74f27b896f, 0x80deb1fe3b1696b1,
        0x9bdc06a725c71235, 0xc19bf174cf692694,
        0xe49b69c19ef14ad2, 0xefbe4786384f25e3,
        0x0fc19dc68b8cd5b5, 0x240ca1cc77ac9c65,
        0x2de92c6f592b0275, 0x4a7484aa6ea6e483,
        0x5cb0a9dcbd41fbd4, 0x76f988da831153b5,
        0x983e5152ee66dfab, 0xa831c66d2db43210,
        0xb00327c898fb213f, 0xbf597fc7beef0ee4,
        0xc6e00bf33da88fc2, 0xd5a79147930aa725,
        0x06ca6351e003826f, 0x142929670a0e6e70,
        0x27b70a8546d22ffc, 0x2e1b21385c26c926,
        0x4d2c6dfc5ac42aed, 0x53380d139d95b3df,
        0x650a73548baf63de, 0x766a0abb3c77b2a8,
        0x81c2c92e47edaee6, 0x92722c851482353b,
        0xa2bfe8a14cf10364, 0xa81a664bbc423001,
        0xc24b8b70d0f89791, 0xc76c51a30654be30,
        0xd192e819d6ef5218, 0xd69906245565a910,
        0xf40e35855771202a, 0x106aa07032bbd1b8,
        0x19a4c116b8d2d0c8, 0x1e376c085141ab53,
        0x2748774cdf8eeb99, 0x34b0bcb5e19b48a8,
        0x391c0cb3c5c95a63, 0x4ed8aa4ae3418acb,
        0x5b9cca4f7763e373, 0x682e6ff3d6b2b8a3,
        0x748f82ee5defb2fc, 0x78a5636f43172f60,
        0x84c87814a1f0ab72, 0x8cc702081a6439ec,
        0x90befffa23631e28, 0xa4506cebde82bde9,
        0xbef9a3f7b2c67915, 0xc67178f2e372532b,
        0xca273eceea26619c, 0xd186b8c721c0c207,
        0xeada7dd6cde0eb1e, 0xf57d4f7fee6ed178,
        0x06f067aa72176fba, 0x0a637dc5a2c898a6,
        0x113f9804bef90dae, 0x1b710b35131c471b,
        0x28db77f523047d84, 0x32caab7b40c72493,
        0x3c9ebe0a15c9bebc, 0x431d67c49c100d4c,
        0x4cc5d4becb3e42b6, (0x597f299cfc657e2a),
        (0x5fcb6fab3ad6faec), (0x6c44198c4a475817)
    ]

    for i in range(80):
        S1 = _rotr(e, 14) ^ _rotr(e, 18) ^ _rotr(e, 41)
        ch = (e & f) ^ ((~e) & g)
        temp1 = (hh + S1 + ch + K[i] + w[i]) & 0xffffffffffffffff
        S0 = _rotr(a, 28) ^ _rotr(a, 34) ^ _rotr(a, 39)
        maj = (a & b) ^ (a & c) ^ (b & c)
        temp2 = (S0 + maj) & 0xffffffffffffffff

        hh = g
        g = f
        f = e
        e = (d + temp1) & 0xffffffffffffffff
        d = c
        c = b
        b = a
        a = (temp1 + temp2) & 0xffffffffffffffff

    return [
        (h[0] + a) & 0xffffffffffffffff,
        (h[1] + b) & 0xffffffffffffffff,
        (h[2] + c) & 0xffffffffffffffff,
        (h[3] + d) & 0xffffffffffffffff,
        (h[4] + e) & 0xffffffffffffffff,
        (h[5] + f) & 0xffffffffffffffff,
        (h[6] + g) & 0xffffffffffffffff,
        (h[7] + hh) & 0xffffffffffffffff,
    ]

class sha512:
    def __init__(self, data=b""):
        self._buffer = b""
        self._counter = 0
        self._h = [
            0x6a09e667f3bcc908, 0xbb67ae8584caa73b,
            0x3c6ef372fe94f82b, 0xa54ff53a5f1d36f1,
            0x510e527fade682d1, 0x9b05688c2b3e6c1f,
            0x1f83d9abfb41bd6b, 0x5be0cd19137e2179,
        ]
        if data:
            self.update(data)

    def update(self, data):
        self._buffer += data
        self._counter += len(data)
        while len(self._buffer) >= 128:
            chunk = self._buffer[:128]
            self._buffer = self._buffer[128:]
            self._h = _sha512_compress(chunk, self._h)

    def digest(self):
        length = self._counter * 8

    # Append the '1' bit
        pad = b"\x80"

    # Pad with zeros until message length ≡ 112 (mod 128)
        pad_len = (112 - (self._counter + 1) % 128) % 128
        pad += b"\x00" * pad_len

    # Append 16-byte length (128-bit big-endian)
        pad += struct.pack(">QQ", 0, length)

        buf = self._buffer + pad

    # Process each full 128-byte block
        for i in range(0, len(buf), 128):
            chunk = buf[i:i+128]
            self._h = _sha512_compress(chunk, self._h)

        out = b"".join(struct.pack(">Q", h) for h in self._h)
        return out


def sha512_digest(msg):
    return sha512(msg).digest()

# TEST
#print(sha512_digest("hello".encode()).hex())

