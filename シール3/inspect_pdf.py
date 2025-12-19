import pdfplumber

pdf_path = "/Users/joeyamazaki/Library/Mobile Documents/com~apple~CloudDocs/Cursor/01_project/MC/シール3/現品票20251218.pdf"

with pdfplumber.open(pdf_path) as pdf:
    first_page = pdf.pages[0]
    words = first_page.extract_words()
    # Print width of page to determine midpoint
    print(f"Page Width: {first_page.width}, Page Height: {first_page.height}")
    
    # Filter for words on the left side (x0 < midpoint)
    midpoint = first_page.width / 2
    print(f"Midpoint: {midpoint}")
    
    for word in words:
        if word['x1'] < midpoint:
            print(f"Text: {word['text']}, x0: {word['x0']:.2f}, x1: {word['x1']:.2f}, top: {word['top']:.2f}, bottom: {word['bottom']:.2f}")
