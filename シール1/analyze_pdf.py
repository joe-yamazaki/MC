import pdfplumber

pdf_path = "部材シール20250602_233801.pdf"

with pdfplumber.open(pdf_path) as pdf:
    page = pdf.pages[0]
    width = page.width
    height = page.height
    
    col_width = width / 3
    row_height = height / 10
    
    print(f"Page size: {width}x{height}")
    print(f"Cell size: {col_width}x{row_height}")
    
    # Define crop box for the first cell (top-left)
    x0 = 0
    top = 0
    x1 = col_width
    bottom = row_height
    
    print(f"\n--- Cell (0,0) Crop Box: {x0}, {top}, {x1}, {bottom} ---")
    cell00 = page.crop((x0, top, x1, bottom))
    text00 = cell00.extract_text(layout=True)
    print(text00)
    
    print("\n--- Cell (0,0) Words ---")
    words = cell00.extract_words()
    for w in words:
        print(w)

    # Define crop box for the second cell (top-middle)
    x0 = col_width
    x1 = col_width * 2
    
    print(f"\n--- Cell (1,0) Crop Box: {x0}, {top}, {x1}, {bottom} ---")
    cell10 = page.crop((x0, top, x1, bottom))
    text10 = cell10.extract_text(layout=True)
    print(text10)
