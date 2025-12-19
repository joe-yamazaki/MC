import fitz  # PyMuPDF
import csv
import re
import os

def extract_data_from_pdf(pdf_path, output_csv):
    doc = fitz.open(pdf_path)
    results = []
    
    # regex for order number like 155842(1/2) or similar
    order_pattern = re.compile(r'\d{6}\(\d+/\d+\)')
    # regex for dimension pattern like 1392×130× or 660×860×
    dim_regex = re.compile(r'(\d+)[×x]')
    
    last_order_no = ""
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        width = page.rect.width
        left_half_limit = width / 2
        
        blocks = page.get_text("blocks")
        # Sort blocks by vertical position (y0)
        blocks.sort(key=lambda b: b[1])
        
        page_order_no = ""
        # 1. Update order number if found on this page
        for block in blocks:
            x0, y0, x1, y1, text, block_no, block_type = block
            matches = order_pattern.findall(text)
            if matches:
                page_order_no = matches[0]
                last_order_no = page_order_no
                break
        
        current_order_no = page_order_no or last_order_no
        
        # 2. Extract all left-side data blocks
        page_entries = []
        for block in blocks:
            x0, y0, x1, y1, text, block_no, block_type = block
            
            # STRICT LEFT SIDE CHECK: Using x0 instead of x1 to be safer
            if x0 < left_half_limit:
                lines = [line.strip() for line in text.split('\n') if line.strip()]
                if not lines:
                    continue
                
                # Check if this block looks like a data block (contains a dimension pattern)
                if "×" in lines[0] or "x" in lines[0].lower():
                    # Attempt to parse lines
                    # Expected structure: 
                    # line 0: dimension (e.g., 1392×130×)
                    # line 1: product name (e.g., EXﾍﾞｰｽ板-L)
                    # line 2: product name (often repeated)
                    # line 3: quantity (e.g., 2)
                    
                    product_name = ""
                    dimension = ""
                    quantity = ""
                    
                    # Extraction logic
                    dim_match = dim_regex.search(lines[0])
                    if dim_match:
                        dimension = dim_match.group(1)
                    
                    # Find product name (look for non-numeric lines after the first)
                    for i in range(1, len(lines)):
                        if not lines[i].replace(" ", "").isdigit() and "枚" not in lines[i]:
                            product_name = lines[i]
                            break
                    
                    # Find quantity (usually the last line if it's a number)
                    for i in reversed(range(1, len(lines))):
                        clean_line = lines[i].strip()
                        if clean_line.isdigit():
                            quantity = clean_line
                            break
                    
                    if product_name and dimension and quantity and current_order_no:
                        # User clarified: final CSV should be 27 rows (one per record)
                        page_entries.append([current_order_no, product_name, dimension, quantity])
        
        results.extend(page_entries)
    
    # Write to CSV
    with open(output_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(results)
    
    print(f"Extracted {len(results)} rows to {output_csv}")

if __name__ == "__main__":
    pdf_file = "現品票20251218.pdf"
    output_file = "output.csv"
    if os.path.exists(pdf_file):
        extract_data_from_pdf(pdf_file, output_file)
    else:
        print(f"Error: {pdf_file} not found.")
