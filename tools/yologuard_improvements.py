"""
Starter improvements for IF.yologuard
- entropy detection
- common-decoding + rescan
- format parsing (JSON/XML/YAML)
These are lightweight helpers to fold into the scanner pipeline.
"""

import base64
import binascii
import math
import json
import re
from typing import Tuple, List, Optional

def shannon_entropy(data: bytes) -> float:
    """Compute Shannon entropy for a bytes object."""
    if not data:
        return 0.0
    freq = {}
    for b in data:
        freq[b] = freq.get(b, 0) + 1
    entropy = 0.0
    length = len(data)
    for count in freq.values():
        p = count / length
        entropy -= p * math.log2(p)
    return entropy

def looks_like_base64(s: str) -> bool:
    """Quick heuristic for base64-looking strings."""
    s = s.strip()
    if len(s) < 8:
        return False
    b64_re = re.compile(r'^[A-Za-z0-9+/=\n\r]+$')
    return bool(b64_re.match(s))

def try_decode_base64(s: str) -> Optional[bytes]:
    """Try to decode base64, return bytes or None."""
    try:
        padded = s + "=" * ((4 - len(s) % 4) % 4)
        return base64.b64decode(padded, validate=False)
    except Exception:
        return None

def try_decode_hex(s: str) -> Optional[bytes]:
    s = re.sub(r'[^0-9a-fA-F]', '', s)
    if len(s) % 2 != 0:
        return None
    try:
        return binascii.unhexlify(s)
    except Exception:
        return None

def extract_json_candidates(text: str) -> List[str]:
    """Find JSON-like substrings (naive)."""
    candidates = []
    for m in re.finditer(r'\{[^\{\}]{10,}\}', text, flags=re.DOTALL):
        fragment = m.group(0)
        try:
            json.loads(fragment)
            candidates.append(fragment)
        except Exception:
            pass
    return candidates

def scan_text_with_regexes(text: str, regexes: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
    matches = []
    for name, pattern in regexes:
        for m in re.finditer(pattern, text):
            matches.append((name, m.group(0)))
    return matches

def predecode_and_rescan(text: str, regexes: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
    results = scan_text_with_regexes(text, regexes)
    tokens = re.split(r'[\s\"\'\<\>\(\)\[\]\{\},;:\\]+', text)
    for t in tokens:
        if not t or len(t) < 8:
            continue
        if looks_like_base64(t):
            dec = try_decode_base64(t)
            if dec:
                try:
                    dec_text = dec.decode('utf-8', errors='ignore')
                except Exception:
                    dec_text = ''
                if dec_text:
                    results.extend(scan_text_with_regexes(dec_text, regexes))
        dec_hex = try_decode_hex(t)
        if dec_hex:
            try:
                dec_text = dec_hex.decode('utf-8', errors='ignore')
            except Exception:
                dec_text = ''
            if dec_text:
                results.extend(scan_text_with_regexes(dec_text, regexes))
        ent = shannon_entropy(t.encode('utf-8', errors='ignore'))
        if ent > 4.5 and len(t) >= 16:
            try:
                dec = try_decode_base64(t)
                if dec:
                    results.extend(scan_text_with_regexes(dec.decode('utf-8', errors='ignore'), regexes))
            except Exception:
                pass
    json_cands = extract_json_candidates(text)
    for jc in json_cands:
        try:
            obj = json.loads(jc)
            def walk(o):
                if isinstance(o, dict):
                    for v in o.values():
                        walk(v)
                elif isinstance(o, list):
                    for v in o:
                        walk(v)
                elif isinstance(o, str):
                    results.extend(scan_text_with_regexes(o, regexes))
            walk(obj)
        except Exception:
            pass
    return results

if __name__ == "__main__":
    sample = '{"token":"YWJjZDEyMzQ=","password":"$2b$12$abcdefghijklmnopqrstuv"}'
    regexes = [("generic-token", r"[A-Za-z0-9-_]{16,}"), ("bcrypt", r"\$2[aby]\$\d{2}\$[./A-Za-z0-9]{53}")]
    print(predecode_and_rescan(sample, regexes))
