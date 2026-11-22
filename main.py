#!/usr/bin/env python3
"""Entry point for the make.fun news-image-20261122 entry (v3).

Copies the pre-drawn front page (entry.png, in this repository) to
$MAKEFUN_OUTPUT_DIR/entry.png (default /output/entry.png).

Standard library only; no network; deterministic (byte-identical output
on every run, since it copies a fixed file).
"""

import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    shutil.copyfile(os.path.join(HERE, "entry.png"),
                    os.path.join(out_dir, "entry.png"))


if __name__ == "__main__":
    main()
