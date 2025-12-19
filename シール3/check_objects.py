import pdfplumber

pdf_path = "/Users/joeyamazaki/Library/Mobile Documents/com~apple~CloudDocs/Cursor/01_project/MC/シール3/現品票20251218.pdf"

with pdfplumber.open(pdf_path) as pdf:
    page = pdf.pages[0]
    print(f"Number of images: {len(page.images)}")
    print(f"Number of rects: {len(page.rects)}")
    print(f"Number of lines: {len(page.lines)}")
    print(f"Number of curves: {len(page.curves)}")
    
    if len(page.images) > 0:
        for i, img in enumerate(page.images):
            print(f"Image {i}: {img}")
    
    # Check if there are any objects in the area where "防火戸用" should be
    # T40 is at x=34, top=196. next text is at x=247.
    # Let's see if there are curves or paths in that x-range (50 to 240)
    objs = page.within_bbox((52, 190, 240, 210)).curves
    print(f"Number of curves in the area: {len(objs)}")
