# liboqs Quantum-Resistant Cryptography Deployment

## Overview

**liboqs** (Open Quantum Safe) provides quantum-resistant cryptographic algorithms for post-quantum security.

- **Build Date**: December 3, 2025
- **Source**: Host build artifact `/tmp/liboqs.zip`

## Deployment Status

| Container | Status | Version | Library Path |
|-----------|--------|---------|--------------|
| pct 201 | Installed | 0.15.0 | `/usr/local/lib/liboqs.so.0.15.0` (.so.9, .a, pkgconfig/CMake) |
| pct 200 | Installed | 0.10.1 | `/usr/local/lib/liboqs.a` |

**Note**: pct 201 has the shared library (.so), pct 200 has static library (.a) only.

## Installation Procedure

### Prerequisites
```bash
sudo apt-get update
sudo apt-get install -y unzip pkg-config
```

### From Host (Proxmox)
```bash
# Push artifact to container
pct push 200 /tmp/liboqs.zip /home/setup/liboqs.zip
```

### Inside Container (pct 200)
```bash
# Extract to system directories
sudo unzip ~/liboqs.zip -d /

# Update library cache
sudo ldconfig

# Verify installation
ls -la /usr/local/lib/liboqs*
pkg-config --modversion liboqs
```

### Expected Output (pct 200)
```
/usr/local/lib/liboqs.a
0.10.1
```

### Expected Output (pct 201)
```
/usr/local/lib/liboqs.so -> liboqs.so.0
/usr/local/lib/liboqs.so.0 -> liboqs.so.0.15.0
/usr/local/lib/liboqs.so.0.15.0
0.15.0
```

## Library Contents

The `liboqs.zip` artifact contains:
- `/usr/local/lib/liboqs.so.0.15.0` - Main shared library
- `/usr/local/lib/liboqs.so.0` - Symlink
- `/usr/local/lib/liboqs.so` - Development symlink
- `/usr/local/lib/pkgconfig/liboqs.pc` - pkg-config file
- `/usr/local/include/oqs/` - Header files

## Supported Algorithms

### Key Encapsulation Mechanisms (KEMs)
- CRYSTALS-Kyber (NIST selected)
- BIKE
- Classic McEliece
- FrodoKEM
- HQC
- NTRU
- NTRU Prime
- SABER

### Digital Signatures
- CRYSTALS-Dilithium (NIST selected)
- Falcon (NIST selected)
- SPHINCS+ (NIST selected)

## IF.bus Integration

For IF.bus quantum-safe messaging:

```python
# Example: Quantum-safe key exchange for IF.bus channels
from oqs import KeyEncapsulation

# Initialize Kyber-1024 (highest security level)
kem = KeyEncapsulation("Kyber1024")

# Generate keypair
public_key = kem.generate_keypair()

# Encapsulate (sender)
ciphertext, shared_secret = kem.encap_secret(public_key)

# Decapsulate (receiver)
shared_secret = kem.decap_secret(ciphertext)
```

## Python Bindings

```bash
pip install liboqs-python
```

```python
import oqs

# List available algorithms
print(oqs.get_enabled_kem_mechanisms())
print(oqs.get_enabled_sig_mechanisms())
```

## Verification Commands

```bash
# Check library is loadable
ldconfig -p | grep liboqs

# Check pkg-config
pkg-config --libs --cflags liboqs

# Test with Python
python3 -c "import oqs; print(oqs.get_enabled_kem_mechanisms())"
```

## Troubleshooting

### Library not found
```bash
sudo ldconfig
export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH
```

### pkg-config not finding liboqs
```bash
export PKG_CONFIG_PATH=/usr/local/lib/pkgconfig:$PKG_CONFIG_PATH
```

## Security Notes

- liboqs implements experimental/pre-standardization algorithms
- NIST selected algorithms (Kyber, Dilithium, Falcon, SPHINCS+) are recommended for production
- Keep updated as NIST finalizes post-quantum standards

## References

- [Open Quantum Safe](https://openquantumsafe.org/)
- [liboqs GitHub](https://github.com/open-quantum-safe/liboqs)
- [NIST Post-Quantum Cryptography](https://csrc.nist.gov/projects/post-quantum-cryptography)

---
*IF.ops Crypto Infrastructure*
*Citation: if://ops/crypto/liboqs/v0.15.0*
*Last Updated: 2025-12-04*
*pct 200 Installation: 2025-12-04*
