"""Pre-render the portfolio PDF to WebP page images for the web viewer.

The source PDF carries one 1754x2480 lossless PNG per page (150 DPI A3), which
is why decoding it in the browser was so slow -- roughly 4.4 megapixels of zlib
per page. Re-encoding the same pixels as WebP q80 keeps the resolution and cuts
the payload by about 8x.

Usage:
    pip install pymupdf pillow
    python tools/render-pages.py

Writes pages/NN.webp (full) and pages/NN-sm.webp (half width) and prints the
page count, which must match TOTAL in index.html.
"""

import os
import sys

import pymupdf
from PIL import Image

SOURCE = "Nikhil_Narendiran_portfolio.pdf"
OUT_DIR = "pages"
DPI = 150      # matches the resolution already embedded in the PDF
QUALITY = 80   # visually lossless for this content at display size


def main() -> int:
    if not os.path.exists(SOURCE):
        print("missing source: %s" % SOURCE, file=sys.stderr)
        return 1

    os.makedirs(OUT_DIR, exist_ok=True)
    doc = pymupdf.open(SOURCE)
    full_bytes = small_bytes = 0

    for i in range(doc.page_count):
        pix = doc[i].get_pixmap(dpi=DPI)
        img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)

        full = os.path.join(OUT_DIR, "%02d.webp" % (i + 1))
        img.save(full, "WEBP", method=6, quality=QUALITY)
        full_bytes += os.path.getsize(full)

        small = os.path.join(OUT_DIR, "%02d-sm.webp" % (i + 1))
        img.resize((img.width // 2, img.height // 2), Image.LANCZOS).save(
            small, "WEBP", method=6, quality=QUALITY
        )
        small_bytes += os.path.getsize(small)

    print("pages rendered: %d  (set TOTAL in index.html to this)" % doc.page_count)
    print("full  %5.1f MB" % (full_bytes / 1e6))
    print("small %5.1f MB" % (small_bytes / 1e6))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
