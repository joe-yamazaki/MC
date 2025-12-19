import fitz

pdf_path = "/Users/joeyamazaki/Library/Mobile Documents/com~apple~CloudDocs/Cursor/01_project/MC/シール3/現品票20251218.pdf"

doc = fitz.open(pdf_path)
page = doc[0]

# get_text("text") might work better than blocks or words sometimes
text = page.get_text()
print("--- Full Text ---")
print(text)

doc.close()
