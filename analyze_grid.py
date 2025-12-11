import pdfplumber
from collections import Counter

pdf_path = "部材シール20250602_233801.pdf"

with pdfplumber.open(pdf_path) as pdf:
    page = pdf.pages[0]
    words = page.extract_words()
    
    # Collect Y coordinates (top)
    y_coords = [w['top'] for w in words]
    y_coords.sort()
    
    print(f"Total words: {len(words)}")
    print("Top 20 Y-coordinates:")
    for y in y_coords[:20]:
        print(f"{y:.2f}")
        
    print("\n--- Text Grouping by Y ---")
    # Group words by similar Y (within 2 units) to identify lines
    lines = []
    current_line_y = -1
    current_line_text = []
    
    sorted_words = sorted(words, key=lambda w: (w['top'], w['x0']))
    
    for w in sorted_words:
        if current_line_y == -1 or abs(w['top'] - current_line_y) < 5:
            current_line_text.append(w['text'])
            if current_line_y == -1:
                current_line_y = w['top']
        else:
            print(f"Y={current_line_y:.2f}: {' '.join(current_line_text)}")
            current_line_text = [w['text']]
            current_line_y = w['top']
            
    if current_line_text:
        print(f"Y={current_line_y:.2f}: {' '.join(current_line_text)}")
