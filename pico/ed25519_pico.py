# solana_cold_wallet.py
# Complete Ed25519 implementation for Solana on Raspberry Pi Pico
# Pure Python - No dependencies

#import hashlib
import os
from sha512 import sha512_digest

# Curve constants
q = 2**255 - 19
l = 2**252 + 27742317777372353535851937790883648493

# Helpers
def H(m):
    return sha512_digest(m)

def expmod(b, e, m):
    """FAST modular exponentiation using built-in pow"""
    return pow(b, e, m)

def inv(x):
    return expmod(x, q - 2, q)

# Edwards curve parameters
d = -121665 * inv(121666) % q

# Base point (standard Ed25519)
Bx = 15112221349535400772501151409588531511454012693041857206046113283949847762202
By = 46316835694926478169428394003475163141307993866256225615783033603165251855960

def edwards_add(P, Q):
    """Edwards addition formula"""
    x1, y1 = P
    x2, y2 = Q
    
    x1y2 = x1 * y2 % q
    x2y1 = x2 * y1 % q
    x1x2 = x1 * x2 % q
    y1y2 = y1 * y2 % q
    dx1x2y1y2 = d * x1x2 * y1y2 % q
    
    x3 = (x1y2 + x2y1) * inv(1 + dx1x2y1y2) % q
    y3 = (y1y2 + x1x2) * inv(1 - dx1x2y1y2) % q
    return (x3, y3)

def scalarmult(P, e):
    """Double-and-add algorithm"""
    if e == 0:
        return (0, 1)
    
    Q = (0, 1)  # Identity point
    addend = P
    
    while e:
        if e & 1:
            Q = edwards_add(Q, addend)
        addend = edwards_add(addend, addend)
        e >>= 1
    
    return Q

# Encode/decode points
def encodepoint(P):
    x, y = P
    y_bytes = y.to_bytes(32, 'little')
    if x & 1:
        y_bytes = bytearray(y_bytes)
        y_bytes[31] |= 0x80
        y_bytes = bytes(y_bytes)
    return y_bytes

def decodepoint(s):
    y_bytes = bytearray(s)
    sign_bit = (y_bytes[31] >> 7) & 1
    y_bytes[31] &= 0x7F
    y = int.from_bytes(y_bytes, 'little')
    
    # Recover x
    y2 = y * y % q
    u = (y2 - 1) % q
    v = (d * y2 + 1) % q
    x2 = u * inv(v) % q
    
    x = expmod(x2, (q + 3) // 8, q)
    if (x * x - x2) % q != 0:
        x = (x * pow(2, (q - 1) // 4, q)) % q
    
    if (x & 1) != sign_bit:
        x = q - x
    
    # Verify point is on curve
    if (-x*x + y*y - 1 - d*x*x*y*y) % q != 0:
        raise ValueError("Point not on curve")
    
    return (x, y)

# BYTE-LEVEL CLAMPING - CORRECTED VERSION
def clamp_scalar(hash_bytes):
    """Byte-level clamping as per Ed25519 spec - FIXED"""
    clamped = bytearray(hash_bytes[:32])
    
    # Clear the lowest three bits (make it divisible by 8)
    clamped[0] &= 0xF8
    
    # Clear the highest bit
    clamped[31] &= 0x7F
    
    # Set the second highest bit
    clamped[31] |= 0x40
    
    return bytes(clamped)

# Main Ed25519 operations
def generate_keypair(seed=None):
    """Generate keypair from seed (random if None)"""
    if seed is None:
        seed = os.urandom(32)
    elif len(seed) != 32:
        raise ValueError("Seed must be 32 bytes")
    
    h = H(seed)
    a_bytes = clamp_scalar(h[:32])
    a = int.from_bytes(a_bytes, 'little')
    
    A = scalarmult((Bx, By), a)
    return seed, encodepoint(A)

def sign(secret_key, msg):
    if len(secret_key) != 32:
        raise ValueError("Secret key must be 32 bytes")
    
    h = H(secret_key)
    a_bytes = clamp_scalar(h[:32])
    a = int.from_bytes(a_bytes, 'little')
    
    # Compute r = H(h[32:], message) mod l
    r = H(h[32:] + msg)
    r = int.from_bytes(r, 'little') % l
    
    R = scalarmult((Bx, By), r)
    R_enc = encodepoint(R)
    
    A = scalarmult((Bx, By), a)
    A_enc = encodepoint(A)
    
    # Compute k = H(R_enc, A_enc, message) mod l
    k = H(R_enc + A_enc + msg)
    k = int.from_bytes(k, 'little') % l
    
    S = (r + k * a) % l
    return R_enc + S.to_bytes(32, 'little')

def verify(public_key, msg, signature):
    if len(public_key) != 32 or len(signature) != 64:
        return False
    
    try:
        A = decodepoint(public_key)
        R = decodepoint(signature[:32])
        S = int.from_bytes(signature[32:], 'little')
        
        if S >= l:
            return False
        
        k = H(signature[:32] + public_key + msg)
        k = int.from_bytes(k, 'little') % l
        
        P1 = scalarmult((Bx, By), S)
        P2 = edwards_add(R, scalarmult(A, k))
        
        return P1 == P2
        
    except (ValueError, Exception):
        return False

# ============================================================================
# SOLANA COLD WALLET SPECIFIC FUNCTIONS
# ============================================================================

def create_solana_wallet():
    """Create a new Solana wallet - returns (seed, public_key)"""
    seed = os.urandom(32)
    private_key, public_key = generate_keypair(seed)
    return seed.hex(), public_key.hex()

def solana_sign_transaction(seed, transaction_data):
    """Sign Solana transaction data with seed"""
    private_key, public_key = generate_keypair(seed)
    signature = sign(private_key, transaction_data)
    return signature.hex(), public_key.hex()

def solana_verify_signature(public_key_hex, transaction_data, signature_hex):
    """Verify Solana transaction signature"""
    public_key_bytes = bytes.fromhex(public_key_hex)
    signature_bytes = bytes.fromhex(signature_hex)
    return verify(public_key_bytes, transaction_data, signature_bytes)

def seed_to_public_key(seed_hex):
    """Get public key from seed without exposing private key (hex input)"""
    seed_bytes = bytes.fromhex(seed_hex)
    _, public_key = generate_keypair(seed_bytes)
    return public_key.hex()

# speed_test.py
# Simple sign + verify speed test for Pico

