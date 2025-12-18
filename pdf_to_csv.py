import pdfplumber
import csv
import re
import datetime

pdf_path = "部材シール.pdf"
# Generate timestamped output filename
now = datetime.datetime.now()
timestamp = now.strftime("%Y%m%d_%H%M%S")
output_csv = f"output_{timestamp}.csv"

def extract_label_data(text):
    if not text:
        return None
    
    lines = text.split('\n')
    # Filter out empty lines
    lines = [line.strip() for line in lines if line.strip()]
    
    if not lines:
        return None

    product_name = ""
    val1 = ""
    val2 = ""
    val3 = ""
    val4 = ""
    val5 = ""
    val6 = ""
    
    # Iterate through lines to find patterns
    # We assume:
    # - Value line contains "number ( number )" or just numbers
    # - Bottom line contains "hyphen pattern" and "slash pattern"
    # - Product name is the remaining line (usually at the top)
    
    processed_indices = set()
    
    # 1. Find Bottom Line first (most distinct)
    for i, line in enumerate(lines):
        if i in processed_indices: continue
        
        # Check for hyphen pattern AND slash pattern (strongest signal)
        # Pattern: value - value - value (allowing alphanumeric and special chars like ^)
        match_hyphen = re.search(r'([^-\s]+)\s*-\s*([^-\s]+)\s*-\s*([^-\s]+)', line)
        match_slash = re.search(r'(\d+)\s*/\s*(\d+)', line)
        
        if match_hyphen:
            val3 = match_hyphen.group(1)
            val4 = match_hyphen.group(2)
            val5 = match_hyphen.group(3)
            processed_indices.add(i)
            
            # Slash might be on the same line
            if match_slash:
                val6 = f"{match_slash.group(1)}/{match_slash.group(2)}"
            break # Assume only one bottom line
            
    # 2. Find Value Line (middle)
    for i, line in enumerate(lines):
        if i in processed_indices: continue
        
        # Look for "1900 ( 673160)" pattern
        match_middle = re.search(r'(\d+)\s*\(\s*(\d+)\s*\)', line)
        if match_middle:
            val1 = match_middle.group(1)
            val2 = match_middle.group(2)
            processed_indices.add(i)
            break
        
        # Fallback: if we haven't found it, and line starts with a number and looks like values
        # But be careful not to confuse with product name if product name starts with number
        # Usually value line has specific spacing or format.
        # Let's stick to the parens pattern as primary. 
        # If parens are missing, maybe we can look for just a large number?
        
    # 3. Find Product Name (remaining line, usually first)
    for i, line in enumerate(lines):
        if i in processed_indices: continue
        
        # If we already found product name, append? Or just take the first one?
        # Usually product name is the top-most line.
        if not product_name:
            product_name = line
            processed_indices.add(i)
        else:
            # If we have multiple unmatched lines, maybe append them?
            # For now, let's just take the first unmatched line as product name.
            pass

    # Combine val3, val4, val5 with hyphens
    # User requested: 1, 05, 1 -> 1-05-1 (Removed apostrophe)
    val345 = ""
    if val3 and val4 and val5:
        val345 = f"{val3}-{val4}-{val5}"
    
    # Add leading apostrophe to val6
    # User requested: 1/1 -> '1/1
    if val6:
        val6 = f"'{val6}"

    return [product_name, val1, val2, val345, val6]

def main():
    data_rows = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            width = page.width
            height = page.height
            
            col_width = width / 3
            # Fixed row height and margin based on analysis
            # Text starts at ~37, repeats every 72 units.
            # Setting top margin to 20 to comfortably include the top text (37)
            # and row height to 72.
            row_height = 72
            top_margin = 20
            
            for row in range(10):
                for col in range(3):
                    # Calculate coordinates with fixed margin and height
                    x0 = col * col_width
                    top = top_margin + (row * row_height)
                    x1 = (col + 1) * col_width
                    bottom = top + row_height
                    
                    # Crop the cell
                    cell = page.crop((x0, top, x1, bottom))
                    
                    # Extract text
                    text = cell.extract_text(layout=True)
                    
                    # Parse data
                    row_data = extract_label_data(text)
                    
                    if row_data:
                        # Validation: Product name should not look like the bottom row
                        # If the first field matches the hyphen pattern, it's likely garbage or overlap
                        if re.search(r'[A-Za-z0-9]+\s*-\s*[A-Za-z0-9]+\s*-\s*[A-Za-z0-9]+', row_data[0]):
                            continue
                            
                        data_rows.append(row_data)

    # Write to CSV
    with open(output_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        # No header requested, but usually good to have. 
        # The user example didn't show a header, just data: "ﾍﾞｰｽﾊﾞﾝR,1900,673160,1,3,1,1/1"
        # I will write the data directly.
        writer.writerows(data_rows)
        
    print(f"Successfully converted {len(data_rows)} labels to {output_csv}")

if __name__ == "__main__":
    main()
