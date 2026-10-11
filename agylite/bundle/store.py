"""Content hashing for bundle integrity.

Bundled files are stored as plain single-link copies (D-026); integrity comes from the provenance
hashes: `original_hash` (git blob SHA-1, matches the audited upstream) and `bundled_hash` (sha256).
"""
import hashlib


def git_blob_sha1(data: bytes) -> str:
    """Hash git uses for a file's blob; matches the audited upstream inventories."""
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()
