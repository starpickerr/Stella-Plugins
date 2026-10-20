#!/usr/bin/env python3
"""Build signed plugin ZIPs and a url-based catalog for release / R10 smoke.

Run from Stella-Plugins (or any cwd). Requires Stella-Core on PYTHONPATH and
``STELLA_PLUGIN_SIGNING_SECRET``. Writes ``dist/signed/*.zip`` and
``catalog/release.json`` with ``file://`` URLs so first-boot can install without
machine-local ``path`` entries.

Package digests must use Core ``_sha256_tree`` so they match ``write_signed_zip``
and catalog verify (ignore caches/VCS).
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT.parent / "Stella-Core"
DOMAINS = ("bills", "calendar", "tasks", "email", "elearning", "briefing", "automation", "agent-hub")

def main() -> int:
    if str(CORE) not in sys.path:
        sys.path.insert(0, str(CORE))
    from core.plugins.package_ops import _sha256_tree
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
        digest = _sha256_tree(src)
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
