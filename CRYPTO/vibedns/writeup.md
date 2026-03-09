# DNSSEC Weak Key Generation - CTF Writeup

## Challenge Overview

This is a cryptographic vulnerability challenge involving a custom DNSSEC (DNS Security Extensions) implementation. The challenge required exploiting a weak key generation mechanism in a zone signer to forge RRSIG (DNSSEC signature) records and gain access to a protected DNS server.

**Flag:** `upCTF{ev3n_wh3n_1ts_crypto_1ts_alw4ys_Dn5_EDs2SH5yf7465f8e}`

---

## Vulnerability Analysis

### The Core Issue: Weak Random Number Generation for Cryptographic Keys

The vulnerability exists in the zone signer's key generation function:

```python
def generate_zsk(inception_timestamp):
    """
    Generate a Zone Signing Key (ECDSA P-256).
    """
    random.seed(inception_timestamp)  # ← CRITICAL VULNERABILITY
    
    key_bytes = bytes([random.randint(0, 255) for _ in range(32)])
    private_int = int.from_bytes(key_bytes, "big") % (P256_ORDER - 1) + 1
    
    private_key = ec.derive_private_key(private_int, ec.SECP256R1())
    public_key = private_key.public_key()
    
    return private_key, public_key, key_tag
```

### Why This Is Broken

1. **Predictable Seed**: The private key is seeded using the zone's inception timestamp (a Unix timestamp)
2. **Python's `random` Module**: This is NOT cryptographically secure. It's designed for simulations, not security
3. **Deterministic Output**: Given the timestamp, the private key can be completely recovered
4. **No Entropy**: The timestamp is often publicly visible in DNS records (RRSIG fields)

### Correct Approach

Production code should use:
```python
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec

# WRONG (this challenge)
random.seed(timestamp)
key_bytes = bytes([random.randint(0, 255) for _ in range(32)])

# CORRECT
import os
key_bytes = os.urandom(32)  # Cryptographically secure random bytes
```

---

## Exploitation Steps

### Step 1: Reconnaissance - Extract Zone Parameters

Query the DNS server to extract DNSKEY and RRSIG records:

```bash
dig +tcp @46.225.117.62 -p 30011 xstf.pt. DNSKEY
dig +tcp @46.225.117.62 -p 30011 flag.xstf.pt. TXT
```

**Retrieved Parameters:**
- **key_tag:** 65494 (identifier for the signing key)
- **Inception:** 1772980700 (when the key was generated)
- **Expiration:** 1775572700 (when the signature expires)
- **Algorithm:** 13 (ECDSAP256SHA256 per RFC 6605)
- **Zone Name:** `xstf.pt.`

### Step 2: Determine the Private Key Seed

The inception timestamp from the RRSIG is the seed used for key generation. We can verify this by computing the key_tag:

```python
def compute_key_tag(inception_ts):
    P256_ORDER = 0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551
    
    random.seed(inception_ts)
    key_bytes = bytes([random.randint(0, 255) for _ in range(32)])
    private_int = int.from_bytes(key_bytes, "big") % (P256_ORDER - 1) + 1
    privkey = ec.derive_private_key(private_int, ec.SECP256R1())
    pubkey = privkey.public_key()
    
    # Build DNSKEY RDATA and compute key_tag checksum
    pub_raw = pubkey.public_bytes(
        serialization.Encoding.X962, 
        serialization.PublicFormat.UncompressedPoint
    )[1:]
    pubkey_data = struct.pack("!HBB", 256, 3, 13) + pub_raw
    
    ac = sum(pubkey_data[i] << 8 if i % 2 == 0 else pubkey_data[i] 
             for i in range(len(pubkey_data)))
    return ((ac & 0xFFFF) + (ac >> 16)) & 0xFFFF
```

The RRSIG inception timestamp matches! This confirms the seed.

### Step 3: Recover the Private Key

Once we have the seed, we can regenerate the exact private key:

```python
inception_ts = 1772980700
random.seed(inception_ts)
key_bytes = bytes([random.randint(0, 255) for _ in range(32)])
private_int = int.from_bytes(key_bytes, "big") % (P256_ORDER - 1) + 1
private_key = ec.derive_private_key(private_int, ec.SECP256R1(), default_backend())
```

### Step 4: Forge an RRSIG Signature

Now we can sign arbitrary DNS records:

```python
# Data to forge a signature for
name = "flag.xstf.pt."
rtype = "TXT"
ttl = 3600
rdata = "DNSSEC validation required - POST your RRSIG to /verify on this server"

# Build the data to sign according to RFC 4034
rrsig_header = build_rrsig_header(
    rtype, ttl, inception_ts, expiration, key_tag, "xstf.pt."
)
rrset_wire = build_rrset_wire(name, rtype, ttl, [rdata])
data_to_sign = rrsig_header + rrset_wire

# Sign with recovered private key
sig_der = private_key.sign(data_to_sign, ec.ECDSA(hashes.SHA256()))

# Convert DER signature to raw r||s format (RFC 6605)
r, s = decode_dss_signature(sig_der)
raw_sig = r.to_bytes(32, "big") + s.to_bytes(32, "big")
raw_sig_b64 = base64.b64encode(raw_sig).decode()
```

### Step 5: Submit the Forged Signature

POST the forged RRSIG to the verification endpoint:

```python
import urllib.request
import urllib.parse

params = {
    "name": "flag.xstf.pt.",
    "type": "TXT",
    "ttl": "3600",
    "rdata": "DNSSEC validation required - POST your RRSIG to /verify on this server",
    "sig": raw_sig_b64  # Base64-encoded 64-byte r||s signature
}

url = "http://46.225.117.62:30011/verify"
data = urllib.parse.urlencode(params).encode()
req = urllib.request.Request(url, data=data)

response = urllib.request.urlopen(req)
result = json.loads(response.read())

print(result["flag"])  # FLAG EXTRACTED!
```

---

## Technical Deep Dive

### DNSSEC Signature Format (RFC 4034 / RFC 6605)

RRSIG records contain:
- **Type Covered** (2 bytes): Record type being signed (16 for TXT)
- **Algorithm** (1 byte): 13 = ECDSAP256SHA256
- **Labels** (1 byte): Number of labels in FQDN
- **Original TTL** (4 bytes): TTL value
- **Signature Expiration** (4 bytes): Unix timestamp
- **Signature Inception** (4 bytes): Unix timestamp ← **THE SEED**
- **Key Tag** (2 bytes): Checksum of DNSKEY
- **Signer's Name** (variable): Zone name
- **Signature** (64 bytes for P-256): r || s format

### ECDSA P-256 Signing Process

1. Hash the data with SHA-256: `data_hash = SHA256(data_to_sign)`
2. Generate ECDSA signature using private key: `(r, s) = SIGN_ECDSA(data_hash)`
3. Convert to wire format: `r || s` (each 32 bytes for P-256)
4. Encode as base64 for HTTP transmission

### Key Tag Computation (RFC 4034, Appendix B)

```python
def compute_key_tag(dnskey_rdata):
    ac = 0
    for i, byte in enumerate(dnskey_rdata):
        if i % 2 == 0:
            ac += byte << 8
        else:
            ac += byte
    return ((ac & 0xFFFF) + (ac >> 16)) & 0xFFFF
```

This simple checksum (not cryptographic) is used to identify which key signed an RRSIG. The vulnerability is that we can reverse-engineer the inception timestamp from the key_tag through brute force if needed.

---

## Exploitation Code

### Complete Exploit Script

```python
#!/usr/bin/env python3
import random, struct, base64, json, urllib.request, urllib.parse
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric.utils import decode_dss_signature
from cryptography.hazmat.backends import default_backend

# Zone parameters extracted from DNS
inception_ts = 1772980700
expiration = 1775572700
key_tag = 65494
P256_ORDER = 0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551

# Recover private key
random.seed(inception_ts)
key_bytes = bytes([random.randint(0, 255) for _ in range(32)])
private_int = int.from_bytes(key_bytes, "big") % (P256_ORDER - 1) + 1
privkey = ec.derive_private_key(private_int, ec.SECP256R1(), default_backend())

# Build data to sign
from dnssec_signer import build_rrsig_header, build_rrset_wire, ZONE_NAME

name = "flag.xstf.pt."
rtype = "TXT"
ttl = 3600
rdata = "DNSSEC validation required - POST your RRSIG to /verify on this server"

rrsig_header = build_rrsig_header(rtype, ttl, inception_ts, expiration, key_tag, ZONE_NAME)
rrset_wire = build_rrset_wire(name, rtype, ttl, [rdata])
data_to_sign = rrsig_header + rrset_wire

# Sign
sig_der = privkey.sign(data_to_sign, ec.ECDSA(hashes.SHA256()))
r, s = decode_dss_signature(sig_der)
raw_sig = r.to_bytes(32, "big") + s.to_bytes(32, "big")

# Submit
params = {
    "name": name,
    "type": rtype,
    "ttl": str(ttl),
    "rdata": rdata,
    "sig": base64.b64encode(raw_sig).decode()
}
url = "http://46.225.117.62:30011/verify"
data = urllib.parse.urlencode(params).encode()
req = urllib.request.Request(url, data=data)

response = json.loads(urllib.request.urlopen(req).read())
print(response["flag"])
```

---

## Key Insights & Lessons

### 1. Never Use `random` for Cryptography
- `random.Random()` in Python is NOT cryptographically secure
- Always use `secrets` module or `os.urandom()` for crypto
- Cryptographic libraries (cryptography, NaCl) use secure random sources

### 2. Timestamps Are Not Secrets
- Inception timestamps are publicly visible in RRSIG records
- Unix timestamps are easily guessable (esp. common dates: 2022, 2024, etc.)
- Never derive cryptographic keys from public data

### 3. DNSSEC Complexity
- DNSSEC adds security but is complex
- RFC 4034, 6605, 4035 are dense specifications
- Implementation errors can negate all security benefits

### 4. DNS Over TCP
- DNS can run over TCP (RFC 7766) for larger responses
- Useful for zone transfers and testing
- Format: 2-byte length prefix + DNS message

### 5. Verification is Everything
- The server's verification endpoint properly validates signatures
- Only forged RRSIGs signed with the recovered key are accepted
- This confirms exploit success

---

## Remediation

### For Developers

1. **Use Cryptographically Secure Random:**
   ```python
   from secrets import token_bytes
   key_bytes = token_bytes(32)  # Cryptographically secure
   ```

2. **Use Key Derivation Functions (KDF):**
   ```python
   from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
   # Never use timestamps as KDF input
   ```

3. **Separate Key Generation from Seeds:**
   - Generate keys during setup, not per-operation
   - Store keys in proper key management systems
   - Use HSMs for production systems

4. **Validate Cryptographic Practices:**
   - Code review by security experts
   - Cryptography audit
   - Penetration testing

### For System Administrators

1. **Enable DNSSEC Validation** on resolvers
2. **Monitor Key Expiration** dates
3. **Implement Key Rotation** policies
4. **Audit DNS Traffic** for anomalies
5. **Keep DNS Software Updated**

---

## References

- [RFC 4034 - DNSSEC Resource Records](https://tools.ietf.org/html/rfc4034)
- [RFC 6605 - ECDSA for DNSSEC](https://tools.ietf.org/html/rfc6605)
- [RFC 4035 - DNSSEC Protocol](https://tools.ietf.org/html/rfc4035)
- [RFC 7766 - DNS over TCP](https://tools.ietf.org/html/rfc7766)
- [Python `cryptography` Library](https://cryptography.io/)
- [ECDSA P-256 / secp256r1](https://en.wikipedia.org/wiki/Elliptic_Curve_Digital_Signature_Algorithm)

---

## Conclusion

This challenge demonstrates a critical vulnerability: **using predictable, non-cryptographic random number generators for cryptographic key material**. By extracting the zone's inception timestamp from publicly available RRSIG records, we could deterministically regenerate the private key and forge valid signatures.

The exploit required understanding:
- DNSSEC record formats and standards
- ECDSA cryptography and signature verification
- DNS protocol (TCP variant)
- Python's cryptography library
- HTTP API interaction

**Key Takeaway:** In cryptography, entropy matters. Always use cryptographically secure random sources, and never derive security-critical material from public data.

---

**Challenge Solved:** ✅  
**Flag Captured:** `upCTF{ev3n_wh3n_1ts_crypto_1ts_alw4ys_Dn5_EDs2SH5yf7465f8e}`
