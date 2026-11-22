"""Copy the bundled front-page image to the output directory.

Entry point for the make.fun news-image-20261122 bounty. The program
holds the image in the repository and copies it, byte for byte, to
/output/entry.png (or $MAKEFUN_OUTPUT_DIR/entry.png). No network, no
randomness, no input: two runs write identical bytes.
"""

import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def main() -> int:
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    src = os.path.join(HERE, "entry.png")
    dst = os.path.join(out_dir, "entry.png")
    shutil.copyfile(src, dst)
    return 0


if __name__ == "__main__":
    sys.exit(main())
