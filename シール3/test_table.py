import pdfplumber

pdf_path = "/Users/joeyamazaki/Library/Mobile Documents/com~apple~CloudDocs/Cursor/01_project/MC/シール3/現品票20251218.pdf"

with pdfplumber.open(pdf_path) as pdf:
    page = pdf.pages[0]
    # Crop to left side
    left_side = page.within_bbox((0, 0, page.width / 2, page.height))
    
    print("--- Left Side Text ---")
    print(left_side.extract_text())
    
    print("\n--- Tables on Left Side ---")
    tables = left_side.extract_tables()
    for i, table in enumerate(tables):
        print(f"Table {i}:")
        for row in table:
            print(row)
