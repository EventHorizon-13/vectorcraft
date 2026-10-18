#!/usr/bin/env python3
"""Prepare the pinned served-font input for the fork's Web package; never commit fonts."""

import hashlib
from pathlib import Path
import sys
import urllib.request

PIN = "f8d157532fbfaeda587e826d4cd5b21a49186f7c"
BASE = f"https://raw.githubusercontent.com/notofonts/noto-cjk/{PIN}/Sans"
LICENSE_SHA256 = "6a73f9541c2de74158c0e7cf6b0a58ef774f5a780bf191f2d7ec9cc53efe2bf2"
FONTS = [
    ("sc", "SC", "SimplifiedChinese", "Hans,Latn", "2c76254f6fc379fddfce0a7e84fb5385bb135d3e399294f6eeb6680d0365b74b"),
    ("tc", "TC", "TraditionalChinese", "Hant,Latn", "dce08bd4fd91aa8aa76ed8fea4b694c2dfb8550f67871e326843212ddbeb88b4"),
    ("jp", "JP", "Japanese", "Jpan,Latn", "68a3fc98800b2a27b371f2fb79991daf3633bd89309d4ffaa6946fd587f375b5"),
    ("kr", "KR", "Korean", "Kore,Latn", "6bcb2a0703aa137e874fc2dffa85f6c21ba9a67fa329e81b8c801663af7e992a"),
]


def download(url, destination, expected):
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.is_file() and hashlib.sha256(destination.read_bytes()).hexdigest() == expected:
        return
    temporary = destination.with_suffix(destination.suffix + ".download")
    digest = hashlib.sha256()
    total = 0
    try:
        request = urllib.request.Request(url, headers={"User-Agent": "Vectorcraft-dev"})
        with urllib.request.urlopen(request, timeout=90) as response, temporary.open("wb") as output:
            while chunk := response.read(1024 * 1024):
                total += len(chunk)
                if total > 24 * 1024 * 1024:
                    raise ValueError("Font input exceeds the Web package's per-file cap")
                digest.update(chunk)
                output.write(chunk)
        if digest.hexdigest() != expected:
            raise ValueError(f"SHA-256 mismatch for {destination.name}")
        temporary.replace(destination)
    finally:
        temporary.unlink(missing_ok=True)


def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: prepare-fonts.py OUTPUT_DIRECTORY")
    root = Path(sys.argv[1]).resolve()
    catalog = ["# family | style | file | scripts | licence | licence file | sha256 | source"]
    for short, suffix, directory, scripts, checksum in FONTS:
        folder = f"fonts/noto-sans-cjk-{short}"
        filename = f"NotoSansCJK{short}-Regular-{PIN[:7]}.otf"
        relative = f"{folder}/{filename}"
        download(f"{BASE}/OTF/{directory}/NotoSansCJK{short}-Regular.otf", root / relative, checksum)
        license_path = f"{folder}/OFL.txt"
        download(f"{BASE}/LICENSE", root / license_path, LICENSE_SHA256)
        source = f"https://github.com/notofonts/noto-cjk/tree/{PIN}/Sans/OTF/{directory}"
        catalog.append(f"Noto Sans CJK {suffix} | Regular | {relative} | {scripts} | OFL-1.1 | {license_path} | {checksum} | {source}")
    (root / "fonts/manifest.txt").write_text("\n".join(catalog) + "\n", encoding="utf-8")
    print("Verified SC/TC/JP/KR fonts and OFL licenses; served-font manifest is ready.")


if __name__ == "__main__":
    main()
