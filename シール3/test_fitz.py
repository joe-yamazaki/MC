import fitz

pdf_path = "/Users/joeyamazaki/Library/Mobile Documents/com~apple~CloudDocs/Cursor/01_project/MC/シール3/現品票20251218.pdf"

doc = fitz.open(pdf_path)
page = doc[0]
midpoint = page.rect.width / 2

# Extract text in blocks
blocks = page.get_text("blocks")
print("--- Blocks on Left Side ---")
for b in blocks:
    # b = (x0, y0, x1, y1, "text", block_no, block_type)
    if b[2] < midpoint:
        print(f"Rect: {b[:4]}, Text: {repr(b[4])}")

doc.close()
