import pdfplumber

pdf_path = "/Users/joeyamazaki/Library/Mobile Documents/com~apple~CloudDocs/Cursor/01_project/MC/シール3/現品票20251218.pdf"

with pdfplumber.open(pdf_path) as pdf:
    page = pdf.pages[0]
    chars = page.chars
    for char in chars:
        if char['x1'] < page.width / 2:
            print(f"Char: {repr(char['text'])}, x0: {char['x0']:.2f}, top: {char['top']:.2f}")
