import fitz

pdf_path = "/Users/joeyamazaki/Library/Mobile Documents/com~apple~CloudDocs/Cursor/01_project/MC/シール3/現品票20251218.pdf"

doc = fitz.open(pdf_path)
page = doc[0]
midpoint = page.rect.width / 2

words = page.get_text("words")
print(f"Page Width: {page.rect.width}")
print("--- Left Side Words ---")
for w in words:
    # w = (x0, y0, x1, y1, "text", block_no, line_no, word_no)
    if w[2] < midpoint:
        print(f"Rect: ({w[0]:.2f}, {w[1]:.2f}, {w[2]:.2f}, {w[3]:.2f}), Text: {repr(w[4])}")

doc.close()
