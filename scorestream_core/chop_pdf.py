from pdf2image import convert_from_path

pages = convert_from_path(
    "C:/Users/jingx/git_wa/ScoreStream-core/Polonaise.pdf",
    dpi=300,
    grayscale=True,  # higher DPI = more accurate pixel thickness
    poppler_path=r"C:\Program Files\poppler-25.12.0\Library\bin",
)

pages[0].show()

import cv2
import numpy as np


def binarize(pil_img):
    img = np.array(pil_img)
    _, bw = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return bw


def find_white_bands(bw_img, min_height=30, max_height=50, width_tol=1.0):
    """
    width_tol: fraction of width that must be white (1.0 = fully white)
    """
    h, w = bw_img.shape
    white_rows = []

    for y in range(h):
        white_fraction = np.mean(bw_img[y] == 255)
        if white_fraction >= width_tol:
            white_rows.append(y)

    # Group consecutive rows
    bands = []
    start = None

    for y in white_rows:
        if start is None:
            start = y
            prev = y
        elif y == prev + 1:
            prev = y
        else:
            height = prev - start + 1
            if min_height <= height <= max_height:
                bands.append((start, prev))
            start = y
            prev = y

    # Final band
    if start is not None:
        height = prev - start + 1
        if min_height <= height <= max_height:
            bands.append((start, prev))

    return bands


results = []

for page_num, page in enumerate(pages, start=1):
    bw = binarize(page)
    bands = find_white_bands(bw)

    for band in bands:
        results.append(
            {
                "page": page_num,
                "row_start": band[0],
                "row_end": band[1],
                "thickness": band[1] - band[0] + 1,
            }
        )

print(results)

