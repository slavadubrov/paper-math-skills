#!/usr/bin/env python3
"""Download one pinned arXiv version for reading: TeX source, PDF and PDF text.

Usage:
    python3 fetch_arxiv.py 2402.03300v3 /path/to/empty-dir
    python3 fetch_arxiv.py --self-test

Writes into the directory:
    src/        the TeX source (when the authors uploaded it)
    paper.pdf   the PDF of that version
    paper.txt   PDF text, if `pdftotext` is installed (subscripts get flattened)

The downloads are untrusted data. Nothing in them is executed; archives are
extracted with path checks so no file lands outside src/.
"""

import gzip
import io
import re
import shutil
import subprocess
import sys
import tarfile
import urllib.request
from pathlib import Path

ID_RE = re.compile(r"(\d{4}\.\d{4,5}|[a-z-]+(\.[A-Z]{2})?/\d{7})v\d+")
MAX_BYTES = 500 * 1024 * 1024  # refuse archives that unpack beyond this
UA = "paper-math-skills/0.1 (one-off fetch for reading a paper)"


def get(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        body = r.read(MAX_BYTES + 1)
    if len(body) > MAX_BYTES:
        raise ValueError(f"{url} is larger than 500 MB; refusing")
    return body


def safe_extract(tar: tarfile.TarFile, dest: Path) -> list[str]:
    """Extract regular files only, refusing absolute paths, '..' and links."""
    dest = dest.resolve()
    written = []
    total = 0
    for m in tar.getmembers():
        target = (dest / m.name).resolve()
        if not m.isfile() or not target.is_relative_to(dest):
            continue
        total += m.size
        if total > MAX_BYTES:
            raise ValueError("source archive unpacks to more than 500 MB; refusing")
        target.parent.mkdir(parents=True, exist_ok=True)
        with tar.extractfile(m) as src, open(target, "wb") as out:
            shutil.copyfileobj(src, out)
        written.append(str(target.relative_to(dest)))
    return written


def unpack_source(blob: bytes, src_dir: Path) -> list[str]:
    """arXiv e-prints are a gzipped tar, a single gzipped .tex, or a PDF."""
    src_dir.mkdir(parents=True, exist_ok=True)
    if blob[:4] == b"%PDF":
        return []  # no TeX source was uploaded; the PDF is fetched separately
    if blob[:2] == b"\x1f\x8b":
        with gzip.GzipFile(fileobj=io.BytesIO(blob)) as gz:
            blob = gz.read(MAX_BYTES + 1)
        if len(blob) > MAX_BYTES:
            raise ValueError("source archive unpacks to more than 500 MB; refusing")
    try:
        # mode "r:" reads only an uncompressed tar, so a second compression
        # layer inside the gzip cannot bypass the size limit above.
        with tarfile.open(fileobj=io.BytesIO(blob), mode="r:") as tar:
            return safe_extract(tar, src_dir)
    except tarfile.ReadError:
        (src_dir / "main.tex").write_bytes(blob)
        return ["main.tex"]


def fetch(arxiv_id: str, dest: Path) -> None:
    if not ID_RE.fullmatch(arxiv_id):
        sys.exit(f"Need a versioned arXiv ID such as 2402.03300v3, got {arxiv_id!r}")
    if dest.exists() and any(dest.iterdir()):
        sys.exit(f"{dest} is not empty; use a new directory for each download")
    dest.mkdir(parents=True, exist_ok=True)

    try:
        files = unpack_source(get(f"https://arxiv.org/e-print/{arxiv_id}"), dest / "src")
        pdf = get(f"https://arxiv.org/pdf/{arxiv_id}")
        if pdf[:4] != b"%PDF":
            raise ValueError("arXiv did not return a PDF; refusing")
        (dest / "paper.pdf").write_bytes(pdf)
    except Exception:
        shutil.rmtree(dest)  # leave no half-filled directory that blocks a retry
        raise
    if shutil.which("pdftotext"):
        subprocess.run(
            ["pdftotext", str(dest / "paper.pdf"), str(dest / "paper.txt")],
            check=False,
            timeout=300,
        )

    tex = sorted(f for f in files if f.endswith(".tex"))
    print(f"{arxiv_id} -> {dest}")
    print(f"  TeX files: {', '.join(tex) if tex else 'none (no TeX source; use the PDF)'}")
    print(f"  PDF text:  {'paper.txt' if (dest / 'paper.txt').exists() else 'not extracted'}")


def self_test() -> None:
    import tempfile

    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tar:
        for name, data in [
            ("main.tex", b"x"),
            ("../evil.tex", b"y"),
            ("/abs/evil.tex", b"y"),
            ("sec/a.tex", b"z"),
        ]:
            info = tarfile.TarInfo(name)
            info.size = len(data)
            tar.addfile(info, io.BytesIO(data))
        link = tarfile.TarInfo("link.tex")
        link.type, link.linkname = tarfile.SYMTYPE, "/etc/passwd"
        tar.addfile(link)
    with tempfile.TemporaryDirectory() as tmp:
        written = unpack_source(buf.getvalue(), Path(tmp) / "src")
        assert sorted(written) == ["main.tex", "sec/a.tex"], written
        assert not (Path(tmp) / "evil.tex").exists()
        assert not (Path(tmp) / "src" / "link.tex").exists()
        single = unpack_source(gzip.compress(b"\\documentclass{article}"), Path(tmp) / "s2")
        assert single == ["main.tex"]
        assert unpack_source(b"%PDF-1.5 ...", Path(tmp) / "s3") == []
        inner = io.BytesIO()  # an xz tar inside the gzip must not be unpacked
        with tarfile.open(fileobj=inner, mode="w:xz") as tar:
            info = tarfile.TarInfo("big.tex")
            info.size = 1 << 20
            tar.addfile(info, io.BytesIO(bytes(info.size)))
        nested = unpack_source(gzip.compress(inner.getvalue()), Path(tmp) / "s4")
        assert nested == ["main.tex"], nested
        assert (Path(tmp) / "s4" / "main.tex").stat().st_size < 1 << 20
    assert ID_RE.fullmatch("2402.03300v3") and not ID_RE.fullmatch("2402.03300")
    assert not ID_RE.fullmatch("2402.03300v3\n")
    print("self-test passed")


if __name__ == "__main__":
    if sys.argv[1:] == ["--self-test"]:
        self_test()
    elif len(sys.argv) == 3:
        fetch(sys.argv[1], Path(sys.argv[2]))
    else:
        sys.exit(__doc__)
