import fitz
import csv
import re
import os

def extract_pdf_data(input_pdf, output_csv):
    """
    Extracts specific data from the left-hand form of each page in the PDF.
    """
    if not os.path.exists(input_pdf):
        print(f"Error: File not found - {input_pdf}")
        return

    doc = fitz.open(input_pdf)
    all_data = []

    for page_num in range(len(doc)):
        page = doc[page_num]
        midpoint = page.rect.width / 2
        words = page.get_text("words")

        # Group words on the left side
        left_words = [w for w in words if w[2] < midpoint]

        # 1. Extract '製番' (Seiban)
        # Based on inspection, it's usually around top=46.97
        seiban = ""
        for w in left_words:
            # Look for the pattern in the expected region for Seiban
            if 40 < w[1] < 80:
                # Basic check for Seiban format (e.g., 155842(1/2))
                if "(" in w[4] or re.match(r'^\d+', w[4]):
                    seiban = w[4]
                    break

        # 2. Extract item rows (品名, 仕様, 数量)
        # These are located in the table area, roughly between top=190 and top=460
        # We group words by their vertical position (line)
        rows_data = {}
        for w in left_words:
            x0, y0, x1, y1, text = w[0], w[1], w[2], w[3], w[4]
            
            # Table data range
            if 190 < y0 < 460:
                # Use a small threshold to group words on the same line
                line_y = round(y0)
                if line_y not in rows_data:
                    rows_data[line_y] = []
                rows_data[line_y].append(w)

        # Process grouped lines into structured rows
        for line_y in sorted(rows_data.keys()):
            line_words = sorted(rows_data[line_y], key=lambda w: w[0])
            
            # Expected columns:
            # 品名: Left side (x0 ~ 34)
            # 仕様: Middle (x0 ~ 247)
            # 数量: Right side of the left form (x0 ~ 390)
            
            himmey = ""
            shiyou = ""
            suuryou = ""
            
            # Filter words for this row
            for w in line_words:
                x0, text = w[0], w[4]
                if x0 < 150: # 品名 area
                    himmey += text + " "
                elif 200 < x0 < 320: # 仕様 area
                    shiyou += text
                elif 350 < x0 < 410: # 数量 area
                    suuryou = text

            himmey = himmey.strip()
            
            # Extract only the first number from '仕様' (e.g., 660 from 660×860×)
            shiyou_match = re.search(r'^\d+', shiyou)
            shiyou_clean = shiyou_match.group(0) if shiyou_match else ""

            # Only add if we have some data
            if himmey or shiyou_clean or suuryou:
                # Validation: If it's just '品名' or '仕様' header, skip
                if himmey == "品名" or shiyou == "仕様" or suuryou == "数量":
                    continue
                
                # Check for repetitive "T40" or similar that might be part of 品名
                if himmey:
                    all_data.append([seiban, himmey, shiyou_clean, suuryou])

    doc.close()

    # Write to CSV
    with open(output_csv, mode='w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        # No header requested by user, but let's see if they want one next time.
        # User example didn't have a header.
        writer.writerows(all_data)

    print(f"Extraction complete. Data saved to {output_csv}")
    return all_data

if __name__ == "__main__":
    input_file = "/Users/joeyamazaki/Library/Mobile Documents/com~apple~CloudDocs/Cursor/01_project/MC/シール3/現品票20251218.pdf"
    output_file = "/Users/joeyamazaki/Library/Mobile Documents/com~apple~CloudDocs/Cursor/01_project/MC/シール3/output.csv"
    extract_pdf_data(input_file, output_file)
