from pdf2image import convert_from_path
from PIL import Image
import cv2
import numpy as np

# pdf_path = r"C:\Users\jingx\git_wa\ScoreStream-core\scorestream_core\files\Moonlight_Sonata_1_1st_page.pdf"
pdf_path = "Polonaise.pdf"
pages = convert_from_path(
    pdf_path,
    dpi=300,
    grayscale=True,  # higher DPI = more accurate pixel thickness
    poppler_path=r"C:\Program Files\poppler-25.12.0\Library\bin",
)

# pages[0].show()


def binarize(pil_img):
    img = np.array(pil_img)
    _, bw = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return bw


def find_white_bands(bw_img, min_height=5, max_height=100, width_tol=1.0):

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
        thickness = band[1] - band[0] + 1
        results.append(
            {
                "page": page_num,
                "row_start": band[0],
                "row_end": band[1],
                "thickness": thickness,
            }
        )

print(results)


def bands_to_cuts(bands):
    """
    bands: list of (row_start, row_end)
    returns: sorted list of y cut positions
    """
    return sorted((start + end) // 2 for start, end in bands)


def crop_page_into_strips(pil_img, cut_rows, min_height=10):
    """
    pil_img   : PIL.Image
    cut_rows  : list of y coordinates
    min_height: ignore tiny strips
    """
    width, height = pil_img.size
    strips = []

    prev_y = 0

    for y in cut_rows:
        if y - prev_y >= min_height:
            strip = pil_img.crop((0, prev_y, width, y))
            strips.append(strip)
        prev_y = y

    # last strip
    if height - prev_y >= min_height:
        strip = pil_img.crop((0, prev_y, width, height))
        strips.append(strip)

    return strips


all_strips = []

for page_num, page in enumerate(pages, start=1):
    bw = binarize(page)
    bands = find_white_bands(bw)

    if not bands:
        continue

    cuts = bands_to_cuts(bands)
    strips = crop_page_into_strips(page, cuts)

    for i, strip in enumerate(strips):
        all_strips.append({"page": page_num, "index": i, "image": strip})

# merge close bands
min_gap = 350  # <------------------- ADJUST HERE <--------------------
merged = []
for y in sorted(cuts):
    if not merged or y - merged[-1] > min_gap:
        merged.append(y)


for ele in all_strips:
    ele["image"].show()


debug = np.array(page).copy()

for y in merged:
    cv2.line(debug, (0, y), (debug.shape[1], y), 128, 1)


def visualise_width(width):
    cv2.line(debug, (0, 250), (debug.shape[1], 250), (0, 100, 0), 5)
    cv2.line(debug, (0, 250 + width), (debug.shape[1], 250 + width), (0, 100, 0), 5)


visualise_width(600)

Image.fromarray(debug).show()


for item in all_strips:
    fname = f"page_{item['page']}_strip_{item['index']}.png"
    item["image"].save(fname)
