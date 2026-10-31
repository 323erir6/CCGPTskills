"""Bounded, strict Minecraft Java Edition NBT reader (big-endian).

No third-party dependencies. Supports gzip, zlib and raw NBT, including all tags 0..12.
Rejects huge decompression, excessive recursion, truncated data and malformed lists.
"""
from __future__ import annotations
import gzip
import io
import struct
import zlib
from typing import Any

class NBTError(ValueError):
    pass

class Reader:
    def __init__(self, data: bytes, *, max_depth: int = 64, max_items: int = 2_000_000):
        self.buf = memoryview(data)
        self.offset = 0
        self.max_depth = max_depth
        self.max_items = max_items
        self.items = 0

    def read(self, count: int) -> bytes:
        if count < 0 or self.offset + count > len(self.buf):
            raise NBTError("Truncated NBT or invalid length")
        out = self.buf[self.offset:self.offset+count].tobytes()
        self.offset += count
        return out

    def num(self, fmt: str) -> int | float:
        return struct.unpack(">"+fmt, self.read(struct.calcsize(fmt)))[0]

    def string(self) -> str:
        length = self.num("H")
        raw = self.read(length)
        # Modified UTF-8 uses C0 80 for NUL; ordinary names/properties are UTF-8.
        # Replace just the modified-NUL representation and reject other invalid bytes.
        try:
            return raw.replace(b"\xc0\x80", b"\x00").decode("utf-8")
        except UnicodeDecodeError as e:
            raise NBTError("Invalid UTF-8 in NBT string") from e

    def count(self, num: int) -> None:
        if num < 0 or num > self.max_items or self.items + num > self.max_items:
            raise NBTError("NBT collection limit exceeded")
        self.items += num

    def payload(self, tag: int, depth: int = 0) -> Any:
        if depth > self.max_depth:
            raise NBTError("NBT nesting limit exceeded")
        if tag == 1: return self.num("b")
        if tag == 2: return self.num("h")
        if tag == 3: return self.num("i")
        if tag == 4: return self.num("q")
        if tag == 5: return self.num("f")
        if tag == 6: return self.num("d")
        if tag == 7:
            n = self.num("i"); self.count(n)
            return list(self.read(n))
        if tag == 8: return self.string()
        if tag == 9:
            child, length = self.num("B"), self.num("i")
            self.count(length)
            if child not in range(1,13) and not (child == 0 and length == 0):
                raise NBTError("Invalid NBT list element type")
            return [self.payload(child, depth+1) for _ in range(length)]
        if tag == 10:
            value = {}
            while True:
                t = self.num("B")
                if t == 0: break
                if t not in range(1,13): raise NBTError("Unknown NBT tag type")
                name = self.string()
                self.count(1)
                value[name] = self.payload(t,depth+1)
            return value
        if tag in (11,12):
            length = self.num("i"); self.count(length)
            unit = 4 if tag == 11 else 8
            raw = self.read(length*unit)
            return [v[0] for v in struct.iter_unpack(">i" if tag==11 else ">q",raw)]
        raise NBTError(f"Unexpected NBT tag type {tag}")


def _bounded_decompress(data: bytes, max_output: int) -> bytes:
    if data[:2] == b"\x1f\x8b":
        obj = zlib.decompressobj(16+zlib.MAX_WBITS)
    elif len(data)>=2 and data[0]==0x78:
        obj = zlib.decompressobj()
    else:
        if len(data)>max_output: raise NBTError("NBT input exceeds byte limit")
        return data
    try:
        payload = obj.decompress(data, max_output+1)
        if len(payload)>max_output or not obj.eof:
            raise NBTError("NBT decompression limit reached or incomplete stream")
        payload += obj.flush()
        if len(payload)>max_output or obj.unused_data and data[:2] != b"\x1f\x8b":
            raise NBTError("NBT decompression error")
        return payload
    except zlib.error as e:
        raise NBTError("Invalid compressed NBT") from e


def loads(data: bytes, *, max_output: int=64*1024*1024,
          max_depth: int=64, max_items: int=2_000_000) -> dict:
    if len(data)>max_output:
        raise NBTError("Compressed file exceeds configured limit")
    raw = _bounded_decompress(data,max_output)
    reader = Reader(raw,max_depth=max_depth,max_items=max_items)
    if reader.num("B") != 10: raise NBTError("Root NBT tag must be compound")
    reader.string()  # root tag name
    result=reader.payload(10)
    if reader.offset != len(raw): raise NBTError("Unexpected trailing NBT bytes")
    return result
