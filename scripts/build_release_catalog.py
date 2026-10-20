#!/usr/bin/env python3
"""Build signed plugin ZIPs and a url-based catalog for release / R10 smoke.

Run from Stella-Plugins (or any cwd). Requires Stella-Core on PYTHONPATH and
``STELLA_PLUGIN_SIGNING_SECRET``. Writes ``dist/signed/*.zip`` and
``catalog/release.json`` with ``file://`` URLs so first-boot can install without
machine-local ``path`` entries.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT.parent / "Stella-Core"
DOMAINS = ("bills", "calendar", "tasks", "email", "elearning", "briefing", "automation", "agent-hub")

def _package_files(root: Path):
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        if "__pycache__" in path.parts or path.suffix in {".pyc", ".pyo"}:
            continue
        yield path


def _tree_digest(root: Path) -> str:
    h = hashlib.sha256()
    for path in _package_files(root):
        h.update(path.relative_to(root).as_posix().encode("utf-8"))
        h.update(b"\0")
        h.update(path.read_bytes())
        h.update(b"\0")
    return h.hexdigest()


def main() -> int:
    if str(CORE) not in sys.path:
        sys.path.insert(0, str(CORE))
    from core.plugins.signing import write_signed_zip

    secret = os.environ.get("STELLA_PLUGIN_SIGNING_SECRET", "").encode("utf-8")
    if not secret:
        print("STELLA_PLUGIN_SIGNING_SECRET is required", file=sys.stderr)
        return 2

    out_dir = ROOT / "dist" / "signed"
    out_dir.mkdir(parents=True, exist_ok=True)
    catalog_path = ROOT / "catalog" / "release.json"
    plugins = []
    for domain in DOMAINS:
        src = ROOT / "plugins" / domain
        if not src.is_dir():
            print(f"missing {src}", file=sys.stderr)
            return 1
        digest = _tree_digest(src)
        archive = out_dir / f"stella.{domain}-1.0.0.zip"
        write_signed_zip(src, archive, secret=secret)
        # URL is relative to catalog/ so the file stays portable (no machine paths).
        rel_url = os.path.relpath(archive, catalog_path.parent).replace("\\", "/")
        plugins.append(
            {
                "pluginId": f"stella.{domain}",
                "hostApi": "^1.0.0",
                "version": "1.0.0",
                "url": rel_url,
                "sha256": digest,
            }
        )
        print(f"signed {archive.name} sha256={digest[:12]}…")

    catalog = {"coreApi": "1.0.0", "plugins": plugins}
    catalog_path.write_text(json.dumps(catalog, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {catalog_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
