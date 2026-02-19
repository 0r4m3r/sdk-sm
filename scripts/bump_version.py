#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BWS_CARGO_TOML = ROOT / "crates" / "bws" / "Cargo.toml"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Bump bws-cli version in crates/bws/Cargo.toml")
    parser.add_argument("--version", required=True, help="Version to set, for example 2.0.0")
    return parser.parse_args(argv)


def read_bws_version(path: Path) -> str:
    in_package = False
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            in_package = stripped == "[package]"
            continue
        if in_package and stripped.startswith("version"):
            match = re.match(r'version\s*=\s*"([^"]+)"', stripped)
            if not match:
                raise ValueError(f"Unsupported version line: {line!r}")
            return match.group(1)
    raise ValueError("[package] version not found in crates/bws/Cargo.toml")


def set_bws_version(path: Path, new_version: str) -> None:
    lines = path.read_text(encoding="utf-8").splitlines()
    in_package = False
    updated = False
    for idx, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            in_package = stripped == "[package]"
            continue
        if in_package and stripped.startswith("version"):
            match = re.match(r'(\s*version\s*=\s*")([^"]+)(".*)', line)
            if not match:
                raise ValueError(f"Unsupported version line: {line!r}")
            lines[idx] = f"{match.group(1)}{new_version}{match.group(3)}"
            updated = True
            break
    if not updated:
        raise ValueError("[package] version line not found to update in crates/bws/Cargo.toml")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    new_version = args.version.strip()
    if not re.match(r"^[0-9A-Za-z][0-9A-Za-z._+-]*$", new_version):
        print(f"Invalid version string: {new_version}", file=sys.stderr)
        return 2

    old_version = read_bws_version(BWS_CARGO_TOML)
    if old_version == new_version:
        print(f"bws version already {new_version}")
        return 0

    set_bws_version(BWS_CARGO_TOML, new_version)
    print(f"Updated crates/bws/Cargo.toml: {old_version} -> {new_version}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
