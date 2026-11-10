"""Work out how a statement file is encoded without guessing wildly.

Banks send UTF-8 (with or without a byte order mark), UTF-16 (always with
one), Windows-1252 and Latin-1. The rules, in order:

1. A byte order mark decides.
2. An encoding named in the layout decides.
3. If the whole file is valid UTF-8, it is UTF-8.
4. If it is valid Windows-1252, it is Windows-1252 (which covers Latin-1
   text and the smart quotes and euro sign Windows exports add).
5. Otherwise Latin-1, which can decode any bytes.

Steps 3 and 4 read the whole file once, in chunks, so very large files
are not held in memory.
"""

from __future__ import annotations

import codecs
import os

_BOMS = (
    (codecs.BOM_UTF8, "utf-8-sig"),
    (codecs.BOM_UTF32_LE, "utf-32"),
    (codecs.BOM_UTF32_BE, "utf-32"),
    (codecs.BOM_UTF16_LE, "utf-16"),
    (codecs.BOM_UTF16_BE, "utf-16"),
)

_CHUNK = 1 << 20


def _decodes_as(path: str | os.PathLike[str], encoding: str) -> bool:
    decoder = codecs.getincrementaldecoder(encoding)(errors="strict")
    try:
        with open(path, "rb") as fh:
            while chunk := fh.read(_CHUNK):
                decoder.decode(chunk)
            decoder.decode(b"", final=True)
    except UnicodeDecodeError:
        return False
    return True


def detect_encoding(path: str | os.PathLike[str], declared: str | None = None) -> str:
    """Return the codec name to open ``path`` with."""
    with open(path, "rb") as fh:
        head = fh.read(4)
    for bom, name in _BOMS:
        if head.startswith(bom):
            return name
    if declared and declared.lower() != "auto":
        try:
            codecs.lookup(declared)
        except LookupError:
            raise ValueError(f"unknown encoding {declared!r} in layout") from None
        return declared
    if _decodes_as(path, "utf-8"):
        return "utf-8"
    if _decodes_as(path, "cp1252"):
        return "cp1252"
    return "latin-1"
