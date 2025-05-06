from zlib import crc32

def encode_string(s: str) -> int:
    """Encodes a string using CRC32 and returns the checksum as an integer."""
    return crc32(str.encode(s))